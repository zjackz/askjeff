// Sorftime Test Page - Quick Examples
// 为每个 API 端点提供快速示例数据

export const API_EXAMPLES = {
    'product': {
        asins: 'B08N5WRWNW',
        domain: 1,
        trend: 1,
        description: '查询 Amazon Echo Dot (4th Gen) 的完整产品信息'
    },
    'category': {
        nodeId: '172282',
        domain: 1,
        description: '查询 Electronics 类目的 Best Sellers Top 100'
    },
    'category-tree': {
        domain: 1,
        description: '获取完整的类目树结构（数据量大，约10MB+）'
    },
    'category-trend': {
        nodeId: '172282',
        trendIndex: 0,
        domain: 1,
        description: '查询 Electronics 类目的销量趋势数据'
    },
    'category-products': {
        nodeId: '172282',
        page: 1,
        domain: 1,
        description: '分页查询类目产品列表'
    },
    'product-query': {
        queryType: 1,
        pattern: 'wireless headphones',
        page: 1,
        domain: 1,
        description: '搜索无线耳机相关产品'
    },
    'keyword-query': {
        keyword: 'iphone case',
        page: 1,
        domain: 1,
        description: '搜索 "iphone case" 相关关键词'
    },
    'keyword-detail': {
        keyword: 'wireless mouse',
        domain: 1,
        description: '查询 "wireless mouse" 关键词的详细数据'
    },
    'keyword-search-results': {
        keyword: 'laptop stand',
        page: 1,
        domain: 1,
        description: '查询 "laptop stand" 的搜索结果产品'
    },
    'asin-sales-volume': {
        asins: 'B08N5WRWNW',
        queryStart: '2024-01-01',
        queryEnd: '2024-01-31',
        page: 1,
        domain: 1,
        description: '查询产品的官方销量数据'
    },
    'product-variation-history': {
        asins: 'B08N5WRWNW',
        domain: 1,
        description: '查询产品子体变化历史'
    },
    'product-trend': {
        asins: 'B08N5WRWNW',
        queryStart: '2024-01-01',
        queryEnd: '2024-01-31',
        trendIndex: 0,
        domain: 1,
        description: '查询产品趋势数据（功能设计中）'
    },
    'product-realtime': {
        asins: 'B08N5WRWNW',
        update: 24,
        domain: 1,
        description: '实时采集产品数据（24小时内未更新则采集）'
    },
    'product-realtime-status': {
        queryStart: '2024-01-15',
        domain: 1,
        description: '查询实时采集任务状态'
    },
    'reviews-collection': {
        asins: 'B08N5WRWNW',
        mode: 0,
        star: '',
        onlyPurchase: 0,
        page: 1,
        domain: 1,
        description: '实时采集产品评论（按热度排序）'
    },
    'reviews-collection-status': {
        asins: 'B08N5WRWNW',
        update: 24,
        domain: 1,
        description: '查询评论采集任务状态'
    },
    'reviews-query': {
        asins: 'B08N5WRWNW',
        queryStart: '2024-01-01',
        star: '',
        onlyPurchase: 0,
        page: 1,
        domain: 1,
        description: '查询已采集的评论数据'
    },
    'similar-product-realtime': {
        image: 'base64_encoded_image_here',
        domain: 1,
        description: '通过图片搜索相似产品（需要 Base64 编码的图片）'
    },
    'similar-product-status': {
        update: 24,
        domain: 1,
        description: '查询图搜任务状态'
    },
    'similar-product-result': {
        taskId: 'task_id_from_realtime_request',
        domain: 1,
        description: '获取图搜结果'
    },
    'keyword-search-result-trend': {
        keyword: 'wireless earbuds',
        page: 1,
        domain: 1,
        description: '查询关键词搜索结果的趋势数据'
    },
    'category-request-keyword': {
        nodeId: '172282',
        page: 1,
        domain: 1,
        description: '反查类目相关的关键词'
    },
    'asin-request-keyword': {
        asins: 'B08N5WRWNW',
        page: 1,
        domain: 1,
        description: '反查产品相关的关键词'
    },
    'keyword-product-ranking': {
        keyword: 'bluetooth speaker',
        page: 1,
        domain: 1,
        description: '查询关键词下的产品排名'
    },
    'asin-keyword-ranking': {
        keyword: 'wireless charger',
        asins: 'B08N5WRWNW',
        queryStart: '2024-01-01',
        queryEnd: '2024-01-31',
        page: 1,
        domain: 1,
        description: '查询产品在关键词下的排名趋势'
    },
    'coin-query': {
        domain: 1,
        description: '查询当前账户的积分余额'
    },
    'coin-stream': {
        page: 1,
        domain: 1,
        description: '查询积分使用明细'
    },
    'request-stream': {
        page: 1,
        domain: 1,
        description: '查询 Request 使用明细'
    }
}

// 常用 ASIN 示例
export const POPULAR_ASINS = [
    { label: 'Echo Dot (4th Gen)', value: 'B08N5WRWNW' },
    { label: 'Fire TV Stick', value: 'B08C1W5N87' },
    { label: 'Kindle Paperwhite', value: 'B08KTZ8249' },
    { label: 'AirPods Pro', value: 'B09JQMJHXY' },
    { label: 'iPhone 15 Pro', value: 'B0CHX1W1XY' }
]

// 常用类目 NodeId
export const POPULAR_CATEGORIES = [
    { label: 'Electronics', value: '172282' },
    { label: 'Computers & Accessories', value: '541966' },
    { label: 'Home & Kitchen', value: '1055398' },
    { label: 'Sports & Outdoors', value: '3375251' },
    { label: 'Toys & Games', value: '165793011' }
]

// 常用关键词
export const POPULAR_KEYWORDS = [
    'wireless earbuds',
    'laptop stand',
    'phone case',
    'bluetooth speaker',
    'usb c cable',
    'wireless mouse',
    'gaming keyboard',
    'webcam',
    'portable charger',
    'smart watch'
]
