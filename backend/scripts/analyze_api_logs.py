#!/usr/bin/env python3
"""
自动分析最近的 API 调用日志，诊断问题

使用方法（在容器内）：
  cd /app && python3 -c "exec(open('analyze_api_logs.py').read()); main()"
  
或者从宿主机：
  docker exec askjeff-dev-backend-1 bash -c "cd /app && python3 analyze_api_logs.py"
"""
import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

# 确保在 app 目录
if os.path.exists('/app'):
    os.chdir('/app')
    sys.path.insert(0, '/app')

try:
    from sqlalchemy import create_engine, desc
    from sqlalchemy.orm import sessionmaker
    from app.models.log import SystemLog
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保在 Docker 容器内运行此脚本")
    sys.exit(1)

# 数据库连接
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/askjeff')


def analyze_logs(minutes=60, platform=None, limit=50):
    """分析最近的 API 日志"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # 计算时间范围
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        # 构建查询
        query = db.query(SystemLog).filter(
            SystemLog.category == "external_api",
            SystemLog.timestamp >= since
        )
        
        logs = query.order_by(desc(SystemLog.timestamp)).limit(limit).all()
        
        # 如果指定了平台，在 Python 层面过滤
        if platform:
            logs = [log for log in logs if log.context and log.context.get('platform') == platform]
        
        if not logs:
            print(f"\n❌ 最近 {minutes} 分钟内没有找到 API 调用日志")
            if platform:
                print(f"   平台筛选: {platform}")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 API 调用日志分析报告")
        print(f"{'='*80}")
        print(f"时间范围: 最近 {minutes} 分钟")
        print(f"日志总数: {len(logs)}")
        if platform:
            print(f"平台筛选: {platform}")
        print(f"{'='*80}\n")
        
        # 统计分析
        stats = {
            'total': len(logs),
            'success': 0,
            'error': 0,
            'by_platform': defaultdict(int),
            'by_endpoint': defaultdict(int),
            'by_error': defaultdict(int),
            'total_duration': 0,
            'quota_consumed': 0,
            'quota_left': None
        }
        
        errors = []
        
        for log in logs:
            ctx = log.context or {}
            
            # 统计级别
            if log.level == 'info':
                stats['success'] += 1
            else:
                stats['error'] += 1
                errors.append(log)
            
            # 统计平台
            platform_name = ctx.get('platform', 'Unknown')
            stats['by_platform'][platform_name] += 1
            
            # 统计端点
            url = ctx.get('url', '')
            endpoint = url.split('/')[-1].split('?')[0] if url else 'Unknown'
            stats['by_endpoint'][endpoint] += 1
            
            # 统计耗时
            duration = ctx.get('duration_ms', 0)
            if duration:
                stats['total_duration'] += duration
            
            # 统计 Quota
            response = ctx.get('response', {})
            if response:
                consumed = response.get('requestConsumed')
                left = response.get('requestLeft')
                if consumed:
                    stats['quota_consumed'] += consumed
                if left is not None:
                    stats['quota_left'] = left
            
            # 收集错误信息
            if log.level == 'error':
                error_detail = ctx.get('error_detail', {})
                error_key = f"{error_detail.get('api_code', 'N/A')} - {error_detail.get('api_message', 'Unknown')}"
                stats['by_error'][error_key] += 1
        
        # 打印统计信息
        print("📈 统计概览")
        print(f"  ✅ 成功: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
        print(f"  ❌ 失败: {stats['error']} ({stats['error']/stats['total']*100:.1f}%)")
        if stats['total_duration'] > 0:
            print(f"  ⏱️  平均耗时: {stats['total_duration']/stats['total']:.0f}ms")
        if stats['quota_consumed'] > 0:
            print(f"  💰 Quota 消耗: {stats['quota_consumed']}")
        if stats['quota_left'] is not None:
            print(f"  💰 Quota 剩余: {stats['quota_left']}")
        print()
        
        # 按平台统计
        print("🌐 按平台统计")
        for plat, count in sorted(stats['by_platform'].items(), key=lambda x: -x[1]):
            print(f"  {plat}: {count}")
        print()
        
        # 按端点统计
        print("🔗 按端点统计")
        for endpoint, count in sorted(stats['by_endpoint'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {endpoint}: {count}")
        print()
        
        # 错误分析
        if errors:
            print(f"❌ 错误详情 (共 {len(errors)} 条)")
            print(f"{'-'*80}")
            
            for i, log in enumerate(errors[:10], 1):
                ctx = log.context or {}
                print(f"\n[{i}] {log.timestamp.strftime('%H:%M:%S')} - {log.message}")
                
                print(f"    平台: {ctx.get('platform', 'N/A')}")
                print(f"    URL: {ctx.get('url', 'N/A')}")
                print(f"    状态码: {ctx.get('status_code', 'N/A')}")
                print(f"    耗时: {ctx.get('duration_ms', 'N/A')}ms")
                
                error_detail = ctx.get('error_detail', {})
                if error_detail:
                    print(f"    错误码: {error_detail.get('api_code', 'N/A')}")
                    print(f"    错误信息: {error_detail.get('api_message', 'N/A')}")
                
                request = ctx.get('request', {})
                if request:
                    print(f"    请求参数: {str(request)[:100]}")
                
                raw_response = ctx.get('raw_response')
                if raw_response:
                    print(f"    原始响应: {raw_response[:200]}...")
            
            if len(errors) > 10:
                print(f"\n... 还有 {len(errors) - 10} 条错误未显示")
            
            print(f"\n{'-'*80}")
            
            if stats['by_error']:
                print(f"\n📊 错误分类统计")
                for error_type, count in sorted(stats['by_error'].items(), key=lambda x: -x[1]):
                    print(f"  {error_type}: {count}")
        
        # 诊断建议
        print(f"\n{'='*80}")
        print("💡 诊断建议")
        print(f"{'='*80}")
        
        if stats['error'] == 0:
            print("✅ 所有 API 调用都成功，系统运行正常")
        else:
            error_rate = stats['error'] / stats['total'] * 100
            
            if error_rate > 50:
                print(f"⚠️  错误率过高 ({error_rate:.1f}%)，需要紧急处理！")
            elif error_rate > 20:
                print(f"⚠️  错误率较高 ({error_rate:.1f}%)，建议检查")
            else:
                print(f"ℹ️  有少量错误 ({error_rate:.1f}%)，建议关注")
            
            for error_type, count in stats['by_error'].items():
                if 'null' in error_type.lower() or 'none' in error_type.lower() or 'n/a' in error_type.lower():
                    print("\n🔍 发现响应解析失败:")
                    print("   1. 检查 Pydantic 模型字段映射")
                    print("   2. 查看 raw_response 了解实际响应结构")
                    print("   3. 确认字段名大小写是否匹配")
                    break
            
            if stats['quota_left'] is not None and stats['quota_left'] < 100:
                print(f"\n⚠️  API Quota 即将耗尽 (剩余: {stats['quota_left']})")
                print("   建议: 充值或优化调用频率")
        
        if stats['total_duration'] > 0:
            avg_duration = stats['total_duration'] / stats['total']
            if avg_duration > 5000:
                print(f"\n⚠️  API 响应时间过长 (平均: {avg_duration:.0f}ms)")
                print("   建议: 检查网络连接或联系 API 提供方")
        
        print(f"\n{'='*80}\n")
        
    finally:
        db.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='分析 API 调用日志')
    parser.add_argument('--minutes', type=int, default=60, help='分析最近N分钟的日志 (默认: 60)')
    parser.add_argument('--platform', type=str, help='筛选特定平台 (如: Sorftime, DeepSeek)')
    parser.add_argument('--limit', type=int, default=50, help='最多分析N条日志 (默认: 50)')
    
    args = parser.parse_args()
    
    try:
        analyze_logs(minutes=args.minutes, platform=args.platform, limit=args.limit)
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
