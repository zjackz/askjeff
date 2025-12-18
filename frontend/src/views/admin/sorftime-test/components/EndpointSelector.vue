<template>
  <div class="sidebar-header">
    <div class="endpoint-selector">
      <el-tag type="success" effect="dark" size="small" class="method-tag">POST</el-tag>
      <el-select 
        :model-value="modelValue" 
        @update:model-value="$emit('update:modelValue', $event)"
        placeholder="Select Endpoint" 
        filterable 
        size="small" 
        class="endpoint-select"
      >
        <el-option-group label="基础查询 API (1-9)">
          <el-option label="1. ProductRequest (产品详情)" value="product" />
          <el-option label="2. CategoryRequest (类目热销)" value="category" />
          <el-option label="3. CategoryTree (类目树)" value="category-tree" />
          <el-option label="4. CategoryTrend (类目趋势)" value="category-trend" />
          <el-option label="5. CategoryProducts (类目产品)" value="category-products" />
          <el-option label="6. ProductQuery (产品搜索)" value="product-query" />
          <el-option label="7. KeywordQuery (关键词搜索)" value="keyword-query" />
          <el-option label="8. KeywordRequest (关键词详情)" value="keyword-detail" />
          <el-option label="9. KeywordSearchResults (关键词搜索结果)" value="keyword-search-results" />
        </el-option-group>
        
        <el-option-group label="高级数据 API (10-12)">
          <el-option label="10. AsinSalesVolume (ASIN销量)" value="asin-sales-volume" />
          <el-option label="11. ProductVariationHistory (子体历史)" value="product-variation-history" />
          <el-option label="12. ProductTrend (产品趋势)" value="product-trend" />
        </el-option-group>
        
        <el-option-group label="实时采集 API (13-20)">
          <el-option label="13. ProductRealtimeRequest (实时产品)" value="product-realtime" />
          <el-option label="14. ProductRealtimeStatusQuery (实时状态)" value="product-realtime-status" />
          <el-option label="15. ProductReviewsCollection (评论采集)" value="reviews-collection" />
          <el-option label="16. ProductReviewsCollectionStatusQuery (评论状态)" value="reviews-collection-status" />
          <el-option label="17. ProductReviewsQuery (评论查询)" value="reviews-query" />
          <el-option label="18. SimilarProductRealtimeRequest (图搜)" value="similar-product-realtime" />
          <el-option label="19. SimilarProductRealtimeRequestStatusQuery (图搜状态)" value="similar-product-status" />
          <el-option label="20. SimilarProductRealtimeRequestCollection (图搜结果)" value="similar-product-result" />
        </el-option-group>
        
        <el-option-group label="关键词扩展 API (21-25)">
          <el-option label="21. KeywordSearchResultTrend (搜索结果趋势)" value="keyword-search-result-trend" />
          <el-option label="22. CategoryRequestKeyword (类目反查关键词)" value="category-request-keyword" />
          <el-option label="23. ASINRequestKeyword (ASIN反查关键词)" value="asin-request-keyword" />
          <el-option label="24. KeywordProductRanking (产品排名)" value="keyword-product-ranking" />
          <el-option label="25. ASINKeywordRanking (ASIN排名趋势)" value="asin-keyword-ranking" />
        </el-option-group>
        
        <el-option-group label="关键词监控 API (26-30)">
          <el-option label="26. KeywordSubscription (关键词订阅)" value="keyword-subscription" />
          <el-option label="27. KeywordTasks (关键词任务)" value="keyword-tasks" />
          <el-option label="28. KeywordTaskUpdate (更新任务)" value="keyword-task-update" />
          <el-option label="29. KeywordBatchScheduleList (批次列表)" value="keyword-batch-schedule-list" />
          <el-option label="30. KeywordBatchScheduleDetail (批次详情)" value="keyword-batch-schedule-detail" />
        </el-option-group>
        
        <el-option-group label="榜单监控 API (31-34)">
          <el-option label="31. BestSellerListSubscription (榜单订阅)" value="best-seller-list-subscription" />
          <el-option label="32. BestSellerListTask (榜单任务)" value="best-seller-list-task" />
          <el-option label="33. BestSellerListDelete (删除任务)" value="best-seller-list-delete" />
          <el-option label="34. BestSellerListDataCollect (数据采集)" value="best-seller-list-data-collect" />
        </el-option-group>
        
        <el-option-group label="跟卖监控 API (35-39)">
          <el-option label="35. ProductSellerSubscription (跟卖订阅)" value="product-seller-subscription" />
          <el-option label="36. ProductSellerTasks (跟卖任务)" value="product-seller-tasks" />
          <el-option label="37. ProductSellerTaskUpdate (更新任务)" value="product-seller-task-update" />
          <el-option label="38. ProductSellerTaskScheduleList (计划列表)" value="product-seller-task-schedule-list" />
          <el-option label="39. ProductSellerTaskScheduleDetail (计划详情)" value="product-seller-task-schedule-detail" />
        </el-option-group>
        
        <el-option-group label="ASIN订阅 API (40-42)">
          <el-option label="40. AsinSubscription (ASIN订阅)" value="asin-subscription" />
          <el-option label="41. AsinSubscriptionQuery (订阅查询)" value="asin-subscription-query" />
          <el-option label="42. AsinSubscriptionCollection (订阅采集)" value="asin-subscription-collection" />
        </el-option-group>
        
        <el-option-group label="账户/积分 API (43-45)">
          <el-option label="43. CoinQuery (积分查询)" value="coin-query" />
          <el-option label="44. CoinStream (积分明细)" value="coin-stream" />
          <el-option label="45. RequestStream (Request明细)" value="request-stream" />
        </el-option-group>
      </el-select>
    </div>
    
    <div class="toolbar-actions">
      <el-tooltip content="加载示例 (Ctrl+L)" placement="bottom">
        <el-button size="small" @click="$emit('load-example')" :icon="MagicStick">
          示例
        </el-button>
      </el-tooltip>
      <el-tooltip content="请求历史 (Ctrl+H)" placement="bottom">
        <el-button size="small" @click="$emit('show-history')" :icon="Clock">
          历史
          <el-badge v-if="historyCount" :value="historyCount" class="history-badge" />
        </el-button>
      </el-tooltip>
      <el-tooltip content="快捷键帮助 (Ctrl+/)" placement="bottom">
        <el-button size="small" @click="$emit('show-shortcuts')" :icon="QuestionFilled">
          快捷键
        </el-button>
      </el-tooltip>
      <el-tooltip content="请求统计" placement="bottom">
        <el-button size="small" @click="$emit('show-stats')" :icon="DataAnalysis">
          统计
        </el-button>
      </el-tooltip>
    </div>
    
    <el-button 
      type="primary" 
      @click="$emit('send-request')" 
      :loading="loading" 
      size="small" 
      class="send-btn"
    >
      <span v-if="!loading">发送请求</span>
      <span v-else>请求中...</span>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { MagicStick, Clock, QuestionFilled, DataAnalysis } from '@element-plus/icons-vue'

interface Props {
  modelValue: string
  loading: boolean
  historyCount?: number
}

defineProps<Props>()

defineEmits<{
  'update:modelValue': [value: string]
  'load-example': []
  'show-history': []
  'show-shortcuts': []
  'show-stats': []
  'send-request': []
}>()
</script>

<style scoped lang="scss">
.sidebar-header {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
}

.endpoint-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .method-tag {
    flex-shrink: 0;
  }
  
  .endpoint-select {
    flex: 1;
  }
}

.toolbar-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.send-btn {
  width: 100%;
}

.history-badge {
  margin-left: 4px;
}
</style>
