<template>
  <div class="postman-container">
    <div class="main-content">
      <!-- Left Pane: Request Configuration -->
      <div class="pane request-pane">
        <div class="sidebar-header">
          <div class="endpoint-selector">
            <el-tag type="success" effect="dark" size="small" class="method-tag">POST</el-tag>
            <el-select v-model="activeEndpoint" placeholder="Select Endpoint" filterable size="small" class="endpoint-select">
              <el-option-group label="Product APIs">
                <el-option label="/api/ProductRequest (产品详情)" value="product" />
                <el-option label="/api/ProductQuery (产品搜索)" value="product-query" />
              </el-option-group>
              <el-option-group label="Category APIs">
                <el-option label="/api/CategoryRequest (类目热销)" value="category" />
                <el-option label="/api/CategoryTree (类目树)" value="category-tree" />
                <el-option label="/api/CategoryTrend (类目趋势)" value="category-trend" />
              </el-option-group>
              <el-option-group label="Keyword APIs">
                <el-option label="/api/KeywordQuery (关键词搜索)" value="keyword-query" />
                <el-option label="/api/KeywordRequest (关键词详情)" value="keyword-detail" />
              </el-option-group>
            </el-select>
          </div>
          <el-button type="primary" @click="handleSend" :loading="loading" size="small" class="send-btn">
            Send Request
          </el-button>
        </div>

        <div class="sidebar-content">
          <!-- API Info Section -->
          <div class="sidebar-section info-section" v-if="currentDoc">
            <div class="doc-header">
              <span class="doc-title">{{ currentDoc.title }}</span>
              <el-tag size="small" type="info" effect="plain">{{ currentDoc.cost }}</el-tag>
            </div>
            <p class="doc-desc">{{ currentDoc.description }}</p>
            <div class="doc-note" v-if="currentDoc.note">
              <el-icon><Warning /></el-icon>
              <span>{{ currentDoc.note }}</span>
            </div>
          </div>

          <!-- Parameters Section -->
          <div class="sidebar-section params-section">
            <h4 class="section-header">Request Parameters</h4>
            
            <!-- Common Params -->
            <div class="param-group">
              <label>Domain (站点)</label>
              <el-select v-model="form.domain" style="width: 100%">
                <el-option label="US (美国)" :value="1" />
                <el-option label="GB (英国)" :value="2" />
                <el-option label="DE (德国)" :value="3" />
                <el-option label="JP (日本)" :value="7" />
                <el-option label="FR (法国)" :value="4" />
                <el-option label="IN (印度)" :value="5" />
                <el-option label="CA (加拿大)" :value="6" />
                <el-option label="ES (西班牙)" :value="8" />
                <el-option label="IT (意大利)" :value="9" />
                <el-option label="MX (墨西哥)" :value="10" />
                <el-option label="AU (澳洲)" :value="12" />
              </el-select>
            </div>

            <!-- Dynamic Params -->
            <template v-if="activeEndpoint === 'product'">
              <div class="param-group">
                <label>ASINs (逗号分隔)</label>
                <el-input 
                  v-model="form.asins" 
                  type="textarea" 
                  :rows="6"
                  placeholder="B0C135XWWH, B081P4LF73"
                  resize="none"
                />
                <div class="param-tip">
                  支持多ASIN查询，按实际数量扣费。
                </div>
              </div>
            </template>

            <template v-if="activeEndpoint === 'category' || activeEndpoint === 'category-products'">
              <div class="param-group">
                <label>Node ID</label>
                <el-input v-model="form.nodeId" placeholder="e.g. 172282" />
                <div class="param-tip">查询类目 Top100 产品。</div>
              </div>
              <div class="param-group" v-if="activeEndpoint === 'category-products'">
                <label>Page</label>
                <el-input-number v-model="form.page" :min="1" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'category-tree'">
              <div class="empty-param">
                <el-alert title="无需额外参数" type="info" :closable="false" show-icon />
              </div>
            </template>

            <template v-if="activeEndpoint === 'category-trend'">
              <div class="param-group">
                <label>Node ID</label>
                <el-input v-model="form.nodeId" placeholder="e.g. 172282" />
              </div>
              <div class="param-group">
                <label>Trend Index</label>
                <el-input-number v-model="form.trendIndex" :min="0" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'product-query'">
              <div class="param-group">
                <label>Query Type</label>
                <el-select v-model="form.queryType" style="width: 100%">
                  <el-option label="New Release" :value="1" />
                  <el-option label="Movers & Shakers" :value="2" />
                  <el-option label="Most Wished For" :value="3" />
                  <el-option label="Gift Ideas" :value="4" />
                </el-select>
              </div>
              <div class="param-group">
                <label>Pattern (Optional)</label>
                <el-input v-model="form.pattern" placeholder="Filter pattern..." />
              </div>
              <div class="param-group">
                <label>Page</label>
                <el-input-number v-model="form.page" :min="1" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'keyword-query' || activeEndpoint === 'keyword-search-results'">
              <div class="param-group">
                <label>Keyword</label>
                <el-input v-model="form.keyword" placeholder="e.g. iphone case" />
              </div>
              <div class="param-group">
                <label>Page</label>
                <el-input-number v-model="form.page" :min="1" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'keyword-detail'">
              <div class="param-group">
                <label>Keyword</label>
                <el-input v-model="form.keyword" placeholder="e.g. iphone case" />
              </div>
            </template>

            <!-- New Endpoints UI -->
            <template v-if="activeEndpoint === 'asin-sales-volume'">
              <div class="param-group">
                <label>ASIN</label>
                <el-input v-model="form.asins" placeholder="Single ASIN" />
              </div>
              <div class="param-group">
                <label>Start Date (Optional)</label>
                <el-input v-model="form.queryStart" placeholder="yyyy-MM-dd" />
              </div>
              <div class="param-group">
                <label>End Date (Optional)</label>
                <el-input v-model="form.queryEnd" placeholder="yyyy-MM-dd" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'product-variation-history'">
              <div class="param-group">
                <label>ASIN</label>
                <el-input v-model="form.asins" placeholder="Single ASIN" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'product-trend'">
              <div class="param-group">
                <label>ASIN</label>
                <el-input v-model="form.asins" placeholder="Single ASIN" />
              </div>
              <div class="param-group">
                <label>Date Range (Start,End)</label>
                <div style="display: flex; gap: 10px;">
                  <el-input v-model="form.queryStart" placeholder="yyyy-MM-dd" />
                  <el-input v-model="form.queryEnd" placeholder="yyyy-MM-dd" />
                </div>
              </div>
              <div class="param-group">
                <label>Trend Type</label>
                <el-input-number v-model="form.trendIndex" :min="0" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'product-realtime'">
              <div class="param-group">
                <label>ASIN</label>
                <el-input v-model="form.asins" placeholder="Single ASIN" />
              </div>
              <div class="param-group">
                <label>Update Threshold (Hours)</label>
                <el-input-number v-model="form.update" :min="1" :max="120" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'product-realtime-status'">
              <div class="param-group">
                <label>Query Date</label>
                <el-input v-model="form.queryStart" placeholder="yyyy-MM-dd" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'reviews-collection'">
              <div class="param-group">
                <label>ASIN</label>
                <el-input v-model="form.asins" placeholder="Single ASIN" />
              </div>
              <div class="param-group">
                <label>Mode</label>
                <el-select v-model="form.mode" style="width: 100%">
                  <el-option label="Top Reviews" :value="0" />
                  <el-option label="Most Recent" :value="1" />
                </el-select>
              </div>
              <div class="param-group">
                <label>Star Filter (e.g. 1,5)</label>
                <el-input v-model="form.star" placeholder="Optional" />
              </div>
              <div class="param-group">
                <label>Only Purchase</label>
                <el-switch v-model="form.onlyPurchase" :active-value="1" :inactive-value="0" />
              </div>
              <div class="param-group">
                <label>Pages (Cost 1pt/page)</label>
                <el-input-number v-model="form.page" :min="1" :max="10" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'reviews-collection-status'">
              <div class="param-group">
                <label>ASIN</label>
                <el-input v-model="form.asins" placeholder="Single ASIN" />
              </div>
              <div class="param-group">
                <label>Update (Hours)</label>
                <el-input-number v-model="form.update" :min="1" :max="240" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'reviews-query'">
              <div class="param-group">
                <label>ASIN</label>
                <el-input v-model="form.asins" placeholder="Single ASIN" />
              </div>
              <div class="param-group">
                <label>Start Date</label>
                <el-input v-model="form.queryStart" placeholder="yyyy-MM-dd" />
              </div>
              <div class="param-group">
                <label>Star Filter</label>
                <el-input v-model="form.star" placeholder="e.g. 5" />
              </div>
              <div class="param-group">
                <label>Only Purchase</label>
                <el-switch v-model="form.onlyPurchase" :active-value="1" :inactive-value="0" />
              </div>
              <div class="param-group">
                <label>Page</label>
                <el-input-number v-model="form.page" :min="1" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'similar-product-realtime'">
              <div class="param-group">
                <label>Image (Base64)</label>
                <el-input v-model="form.image" type="textarea" :rows="4" placeholder="Base64 string..." />
              </div>
            </template>

            <template v-if="activeEndpoint === 'similar-product-status'">
              <div class="param-group">
                <label>Update (Hours)</label>
                <el-input-number v-model="form.update" :min="1" :max="240" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <template v-if="activeEndpoint === 'similar-product-result'">
              <div class="param-group">
                <label>Task ID</label>
                <el-input v-model="form.taskId" placeholder="Task ID from realtime request" />
              </div>
            </template>

            <!-- Batch 1: Keyword/Page -->
            <template v-if="['keyword-search-result-trend', 'keyword-product-ranking'].includes(activeEndpoint)">
              <div class="param-group">
                <label>Keyword</label>
                <el-input v-model="form.keyword" placeholder="e.g. iphone case" />
              </div>
              <div class="param-group">
                <label>Page</label>
                <el-input-number v-model="form.page" :min="1" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <!-- Batch 2: NodeId/Page -->
            <template v-if="activeEndpoint === 'category-request-keyword'">
              <div class="param-group">
                <label>Node ID</label>
                <el-input v-model="form.nodeId" placeholder="e.g. 172282" />
              </div>
              <div class="param-group">
                <label>Page</label>
                <el-input-number v-model="form.page" :min="1" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <!-- Batch 3: ASIN/Page -->
            <template v-if="activeEndpoint === 'asin-request-keyword'">
              <div class="param-group">
                <label>ASIN</label>
                <el-input v-model="form.asins" placeholder="Single ASIN" />
              </div>
              <div class="param-group">
                <label>Page</label>
                <el-input-number v-model="form.page" :min="1" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <!-- Batch 4: ASIN Keyword Ranking -->
            <template v-if="activeEndpoint === 'asin-keyword-ranking'">
              <div class="param-group">
                <label>Keyword</label>
                <el-input v-model="form.keyword" placeholder="e.g. iphone case" />
              </div>
              <div class="param-group">
                <label>ASIN</label>
                <el-input v-model="form.asins" placeholder="Single ASIN" />
              </div>
              <div class="param-group">
                <label>Date Range (Start,End)</label>
                <div style="display: flex; gap: 10px;">
                  <el-input v-model="form.queryStart" placeholder="yyyy-MM-dd" />
                  <el-input v-model="form.queryEnd" placeholder="yyyy-MM-dd" />
                </div>
              </div>
              <div class="param-group">
                <label>Page</label>
                <el-input-number v-model="form.page" :min="1" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <!-- Batch 5: Subscriptions (Content) -->
            <template v-if="['keyword-subscription', 'best-seller-list-subscription', 'product-seller-subscription', 'asin-subscription'].includes(activeEndpoint)">
              <div class="param-group">
                <label>Content / ASINs</label>
                <el-input 
                  v-model="form.asins" 
                  type="textarea" 
                  :rows="6" 
                  placeholder="Format varies by API. Check docs." 
                />
                <div class="param-tip">
                  Use this field for the complex subscription payload (e.g. "+,ASIN,1|...").
                </div>
              </div>
            </template>

            <!-- Batch 6: Tasks (Page only) -->
            <template v-if="['keyword-tasks', 'best-seller-list-task', 'product-seller-tasks', 'asin-subscription-query'].includes(activeEndpoint)">
              <div class="param-group">
                <label>Page</label>
                <el-input-number v-model="form.page" :min="1" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <!-- Batch 7: Task Update -->
            <template v-if="['keyword-task-update', 'product-seller-task-update'].includes(activeEndpoint)">
              <div class="param-group">
                <label>Task ID</label>
                <el-input v-model="form.taskId" placeholder="Task ID" />
              </div>
              <div class="param-group">
                <label>Update Action</label>
                <el-input-number v-model="form.update" placeholder="0:Modify, 1:Pause, 2:Start, 9:Delete" controls-position="right" style="width: 100%" />
              </div>
            </template>

            <!-- Batch 8: Task ID Only -->
            <template v-if="['keyword-batch-schedule-list', 'product-seller-task-schedule-list', 'best-seller-list-delete', 'keyword-batch-schedule-detail', 'product-seller-task-schedule-detail'].includes(activeEndpoint)">
              <div class="param-group">
                <label>Task / Schedule ID</label>
                <el-input v-model="form.taskId" placeholder="Task ID or Schedule ID" />
              </div>
            </template>

            <!-- Batch 9: Data Collect -->
            <template v-if="activeEndpoint === 'best-seller-list-data-collect'">
              <div class="param-group">
                <label>Task ID</label>
                <el-input v-model="form.taskId" placeholder="Task ID" />
              </div>
              <div class="param-group">
                <label>Query Date</label>
                <el-input v-model="form.queryStart" placeholder="yyyy-MM-dd" />
              </div>
            </template>

            <!-- Batch 10: ASIN Collection -->
            <template v-if="activeEndpoint === 'asin-subscription-collection'">
              <div class="param-group">
                <label>ASINs</label>
                <el-input v-model="form.asins" type="textarea" :rows="4" placeholder="ASINs to collect..." />
              </div>
            </template>

            <!-- Batch 11: Coin/Request Stream -->
            <template v-if="['coin-stream', 'request-stream'].includes(activeEndpoint)">
              <div class="param-group">
                <label>Page</label>
                <el-input-number v-model="form.page" :min="1" controls-position="right" style="width: 100%" />
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Right Pane: Response -->
      <div class="pane response-pane">
        <div class="pane-header response-header">
          <div class="tabs-wrapper">
            <span class="tab-label">Response Body</span>
          </div>
          <div class="status-bar" v-if="responseStatus">
            <!-- HTTP Status -->
            <el-tag :type="responseStatus.code === 200 ? 'success' : 'danger'" size="small" effect="plain">
              HTTP {{ responseStatus.code }}
            </el-tag>
            
            <!-- Business Status -->
            <el-tag 
              v-if="businessStatus" 
              :type="businessStatus.isError ? 'danger' : 'success'" 
              size="small"
              effect="dark"
            >
              API {{ businessStatus.code }}: {{ businessStatus.text }}
            </el-tag>

            <el-tag type="info" size="small">{{ responseStatus.time }}ms</el-tag>
            <el-button size="small" link @click="copyResponse">Copy</el-button>
          </div>
        </div>

        <div class="pane-content relative">
          <div v-if="!response && !loading && !error" class="empty-state">
            <el-empty description="Select an endpoint, configure parameters, and click Send." />
          </div>

          <div v-if="loading" class="loading-overlay">
            <div class="spinner"></div>
          </div>

          <div v-if="error" class="error-message">
            <el-alert title="Network/Server Error" type="error" :description="JSON.stringify(error, null, 2)" show-icon :closable="false" />
          </div>

          <div v-if="response">
            <!-- Business Error Alert -->
            <div v-if="businessStatus && businessStatus.isError" class="mb-4">
              <el-alert
                :title="`API Error: ${businessStatus.text}`"
                type="error"
                show-icon
                :closable="false"
              >
                <p>Code: {{ businessStatus.code }}</p>
                  <p>Message: {{ response.Message || response.message }}</p>
              </el-alert>
            </div>

            <!-- Response View Tabs -->
            <el-tabs v-model="responseViewMode" class="mb-4">
              <!-- Visual View: Adaptive (Detail or Comparison) -->
              <el-tab-pane label="Visual View" name="visual">
                <div v-if="productData && productData.length > 0 && activeEndpoint === 'product'">
                  
                  <!-- Single Product: Detail View -->
                  <div v-if="productData.length === 1" class="detail-view">
                    <div class="detail-header">
                      <div class="detail-img-box">
                        <img v-if="productData[0].Photo && productData[0].Photo.length" :src="productData[0].Photo[0]" class="detail-img" />
                        <div v-else class="img-placeholder">No Image</div>
                      </div>
                      <div class="detail-info">
                        <h2 class="detail-title">{{ productData[0].Title }}</h2>
                        <div class="detail-meta">
                          <el-tag effect="dark">{{ productData[0].ASIN }}</el-tag>
                          <el-tag type="success" effect="plain">{{ productData[0].Brand || 'Unknown Brand' }}</el-tag>
                          <span class="detail-price">{{ formatPrice(productData[0].SalesPrice || 0, form.domain) }}</span>
                        </div>
                        
                        <div class="detail-metrics">
                          <div class="metric-card">
                            <div class="metric-label">Rank</div>
                            <div class="metric-value">#{{ productData[0].Rank }}</div>
                          </div>
                          <div class="metric-card">
                            <div class="metric-label">Ratings</div>
                            <div class="metric-value">{{ productData[0].RatingsCount }}</div>
                            <div class="metric-sub">{{ productData[0].FiveStartRatings }}% 5★</div>
                          </div>
                          <div class="metric-card">
                            <div class="metric-label">LQS</div>
                            <div class="metric-value" :class="productData[0].Lqs >= 8 ? 'text-green' : 'text-orange'">
                              {{ productData[0].Lqs }}
                            </div>
                          </div>
                          <div class="metric-card">
                            <div class="metric-label">Sellers</div>
                            <div class="metric-value">{{ productData[0].SellerCount }}</div>
                          </div>
                        </div>

                        <!-- Specifications (In Header) -->
                        <div class="header-specs" v-if="parseProperty(productData[0].Property).length">
                          <div v-for="(item, idx) in parseProperty(productData[0].Property)" :key="idx" class="spec-tag" :title="item.key">
                            <span class="spec-main">{{ item.value || item.key }}</span>
                            <span class="spec-trans" v-if="getTranslation(item.value || item.key)">{{ getTranslation(item.value || item.key) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="detail-content">
                      <!-- Features & Description Grid -->
                      <div class="info-grid">
                        <div class="detail-section feature-section">
                          <h3>Product Features (卖点)</h3>
                          <ul class="feature-list-lg" v-if="productData[0].Feature && productData[0].Feature.length">
                            <li v-for="(feat, idx) in productData[0].Feature" :key="idx">{{ feat }}</li>
                          </ul>
                          <p v-else class="text-gray">No features available.</p>
                        </div>
                        
                        <div class="detail-section desc-section">
                          <h3>Product Description (描述)</h3>
                          <div class="desc-text" v-if="productData[0].Description">
                            {{ productData[0].Description }}
                          </div>
                          <p v-else class="text-gray">No description available.</p>
                        </div>
                      </div>
                      
                      <div class="detail-section">
                        <h3>Trend Analysis</h3>
                        <div class="charts-container">
                          <div class="chart-wrapper">
                            <div ref="salesChartRef" class="echart-instance"></div>
                          </div>
                          <div class="chart-wrapper">
                            <div ref="priceChartRef" class="echart-instance"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Multiple Products: Comparison Table -->
                  <div v-else class="comparison-container">
                    <el-table :data="productData" border style="width: 100%" height="100%">
                      <!-- Basic Info -->
                      <el-table-column label="Product Info" width="300" fixed>
                        <template #default="{ row }">
                          <div class="product-cell">
                            <div class="product-img">
                              <img v-if="row.Photo && row.Photo.length" :src="row.Photo[0]" class="main-img" />
                              <div v-else class="img-placeholder">No Image</div>
                            </div>
                            <div class="product-details">
                              <div class="product-title" :title="row.Title">{{ row.Title }}</div>
                              <div class="product-meta">
                                <el-tag size="small">{{ row.ASIN }}</el-tag>
                                <span class="brand">{{ row.Brand || 'Unknown Brand' }}</span>
                              </div>
                            </div>
                          </div>
                        </template>
                      </el-table-column>

                      <!-- Core Metrics -->
                      <el-table-column label="Price" width="120" sortable prop="SalesPrice">
                        <template #default="{ row }">
                          <span class="price-text">{{ formatPrice(row.SalesPrice || 0, form.domain) }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column label="Rank" width="100" sortable prop="Rank" />
                      <el-table-column label="Ratings" width="120" sortable prop="RatingsCount">
                        <template #default="{ row }">
                          <span>{{ row.RatingsCount }} ({{ row.FiveStartRatings }}%)</span>
                        </template>
                      </el-table-column>
                      <el-table-column label="LQS" width="80" sortable prop="Lqs">
                        <template #default="{ row }">
                          <el-tag :type="row.Lqs >= 8 ? 'success' : 'warning'">{{ row.Lqs }}</el-tag>
                        </template>
                      </el-table-column>

                      <!-- Product Features (Bullet Points) -->
                      <el-table-column label="Features (卖点)" min-width="400">
                        <template #default="{ row }">
                          <ul class="feature-list" v-if="row.Feature && row.Feature.length">
                            <li v-for="(feat, idx) in row.Feature" :key="idx">{{ feat }}</li>
                          </ul>
                          <span v-else class="text-gray">No features available</span>
                        </template>
                      </el-table-column>

                      <!-- Properties / Specs -->
                      <el-table-column label="Specifications (参数)" min-width="300">
                        <template #default="{ row }">
                          <div v-if="row.Property && row.Property.length" class="specs-list">
                            <el-tag v-for="(prop, idx) in row.Property" :key="idx" size="small" class="spec-tag">{{ prop }}</el-tag>
                          </div>
                          <span v-else class="text-gray">No specs available</span>
                        </template>
                      </el-table-column>
                      
                      <!-- Date -->
                      <el-table-column label="Online Date" width="120" prop="OnlineDate">
                        <template #default="{ row }">
                          {{ row.OnlineDate ? String(row.OnlineDate).replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3') : '-' }}
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>

                </div>
                <div v-else class="empty-state">
                  <el-empty description="No visual data available" />
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="JSON View" name="json">
                 <div class="json-toolbar">
                   <el-select 
                     v-model="jsonViewOptions.selectedKeys" 
                     multiple 
                     collapse-tags 
                     collapse-tags-tooltip
                     placeholder="Filter fields..." 
                     style="width: 300px"
                     clearable
                   >
                     <el-option v-for="key in availableKeys" :key="key" :label="key" :value="key" />
                   </el-select>
                   <div class="toolbar-actions">
                     <el-checkbox v-model="jsonViewOptions.wrap" label="Wrap Lines" border size="small" />
                     <el-checkbox v-model="jsonViewOptions.compact" label="Compact" border size="small" />
                   </div>
                 </div>
                 <div 
                   class="code-viewer-container response-viewer" 
                   :class="{ 'is-compact': jsonViewOptions.compact, 'is-wrap': jsonViewOptions.wrap }"
                 >
                  <pre class="code-viewer" v-html="highlightJson(filteredResponse)"></pre>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, watch, onUnmounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// Types
type EndpointType = 
  | 'product' 
  | 'category' 
  | 'category-tree' 
  | 'category-trend' 
  | 'category-products'
  | 'product-query' 
  | 'keyword-query' 
  | 'keyword-detail'
  | 'keyword-search-results'
  | 'asin-sales-volume'
  | 'product-variation-history'
  | 'product-trend' // New: Added ProductTrend
  | 'product-realtime'
  | 'product-realtime-status'
  | 'reviews-collection'
  | 'reviews-collection-status'
  | 'reviews-query'
  | 'similar-product-realtime'
  | 'similar-product-status'
  | 'similar-product-result'
  | 'keyword-search-result-trend' // 21
  | 'category-request-keyword' // 22
  | 'asin-request-keyword' // 23
  | 'keyword-product-ranking' // 24
  | 'asin-keyword-ranking' // 25
  | 'keyword-subscription' // 26
  | 'keyword-tasks' // 27
  | 'keyword-task-update' // 28
  | 'keyword-batch-schedule-list' // 29
  | 'keyword-batch-schedule-detail' // 30
  | 'best-seller-list-subscription' // 31
  | 'best-seller-list-task' // 32
  | 'best-seller-list-delete' // 33
  | 'best-seller-list-data-collect' // 34
  | 'product-seller-subscription' // 35
  | 'product-seller-tasks' // 36
  | 'product-seller-task-update' // 37
  | 'product-seller-task-schedule-list' // 38
  | 'product-seller-task-schedule-detail' // 39
  | 'asin-subscription' // 40
  | 'asin-subscription-query' // 41
  | 'asin-subscription-collection' // 42
  | 'coin-query' // 43
  | 'coin-stream' // 44
  | 'request-stream' // 45

// State
const activeEndpoint = ref<EndpointType>('product')
const responseViewMode = ref('visual')
const loading = ref(false)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const response = ref<any>(null)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const error = ref<any>(null)
const responseStatus = ref<{ code: number, text: string, time: number } | null>(null)

// Chart Refs
const salesChartRef = ref<HTMLElement | null>(null)
const priceChartRef = ref<HTMLElement | null>(null)
let salesChart: echarts.ECharts | null = null
let priceChart: echarts.ECharts | null = null

const form = reactive({
  domain: 1,
  asins: 'B0C135XWWH',
  nodeId: '',
  trendIndex: 0,
  queryType: 1,
  pattern: '',
  page: 1,
  keyword: '',
  // New params
  queryStart: '',
  queryEnd: '',
  update: 24,
  mode: 0,
  star: '',
  onlyPurchase: 0,
  taskId: '',
  image: '' // Base64 string
})

const apiDocs: Record<EndpointType, { title: string; description: string; note?: string; cost: string }> = {
  'product': {
    title: 'ProductRequest',
    description: '产品（Listing）详情查询。',
    note: '当ASIN不存在或链接变狗时不会返回数据（这种场景下我们为了确保产品状态，会实时抓一次产品详情），request仍然会消耗。',
    cost: '按ASIN数量扣费'
  },
  'category': {
    title: 'CategoryRequest',
    description: '类目Best Sellers查询。查询类目Best Seller Top100产品。',
    cost: '5 request'
  },
  'category-tree': {
    title: 'CategoryTree',
    description: '返回Best Seller类目树结构。',
    note: '这个接口返回数据很大（约为10mb+）建议设置较长请求超时时间。',
    cost: '5 request'
  },
  'category-trend': {
    title: 'CategoryTrend',
    description: '类目趋势数据查询。',
    cost: '5 request'
  },
  'category-products': {
    title: 'CategoryProducts',
    description: '类目全部热销产品。查询类目下全部热销产品，对于长尾类目可返回1000+产品。',
    cost: '5 request'
  },
  'product-query': {
    title: 'ProductQuery',
    description: '多维度产品搜索。',
    cost: '5 request'
  },
  'keyword-query': {
    title: 'KeywordQuery',
    description: '关键词搜索。',
    cost: '5 request'
  },
  'keyword-detail': {
    title: 'KeywordRequest',
    description: '关键词详情查询。',
    cost: '5 request'
  },
  'keyword-search-results': {
    title: 'KeywordSearchResults',
    description: '关键词近15日搜索结果产品。仅支持ABA热搜词。',
    cost: '5 request'
  },
  'asin-sales-volume': {
    title: 'AsinSalesVolume',
    description: '产品官方公布子体销量。查询产品官方公布的子体销量历史数据。',
    cost: '1 request'
  },
  'product-variation-history': {
    title: 'ProductVariationHistory',
    description: '产品子体变化历史数据查询。',
    cost: '1 request'
  },
  'product-trend': {
    title: 'ProductTrend',
    description: '产品趋势数据查询（文档标注：未开发/设计中）。',
    cost: '1 request'
  },
  'product-realtime': {
    title: 'ProductRealtimeRequest',
    description: '产品实时数据查询。如果产品设定时间内未更新过，则实时抓取。',
    cost: '1 积分 (JP: 2积分)'
  },
  'product-realtime-status': {
    title: 'ProductRealtimeRequestStatusQuery',
    description: '产品实时数据查询状态查询。',
    cost: '0 request'
  },
  'reviews-collection': {
    title: 'ProductReviewsCollection',
    description: '实时采集产品评论。仅采集，不返回内容。',
    cost: '按页数扣积分 (1积分/页)'
  },
  'reviews-collection-status': {
    title: 'ProductReviewsCollectionStatusQuery',
    description: '评论实时查询任务状态查询。',
    cost: '0 request'
  },
  'reviews-query': {
    title: 'ProductReviewsQuery',
    description: '查询我们已经收录的产品评论。',
    cost: '5 request'
  },
  'similar-product-realtime': {
    title: 'SimilarProductRealtimeRequest',
    description: '图搜相似产品。通过产品图片实时搜索亚马逊平台上相似产品。',
    cost: '5 积分 (JP: 6积分)'
  },
  'similar-product-status': {
    title: 'SimilarProductRealtimeRequestStatusQuery',
    description: '图搜相似产品任务状态查询。',
    cost: '0 request'
  },
  'similar-product-result': {
    title: 'SimilarProductRealtimeRequestCollection',
    description: '图搜相似产品结果查询。',
    cost: '0 request'
  },
  'keyword-search-result-trend': { title: 'KeywordSearchResultTrend', description: '关键词搜索结果产品趋势', cost: '5 request' },
  'category-request-keyword': { title: 'CategoryRequestKeyword', description: '类目反查关键词', cost: '5 request' },
  'asin-request-keyword': { title: 'ASINRequestKeyword', description: 'ASIN反查关键词', cost: '5 request' },
  'keyword-product-ranking': { title: 'KeywordProductRanking', description: '关键词搜索结果产品排名', cost: '2 request' },
  'asin-keyword-ranking': { title: 'ASINKeywordRanking', description: 'ASIN在关键词下排名趋势', cost: '2 request' },
  'keyword-subscription': { title: 'KeywordSubscription', description: '关键词监控任务注册', cost: '0 request' },
  'keyword-tasks': { title: 'KeywordTasks', description: '关键词监控任务查询', cost: '0 request' },
  'keyword-task-update': { title: 'KeywordTaskUpdate', description: '修改关键词监控任务', cost: '0 request' },
  'keyword-batch-schedule-list': { title: 'KeywordBatchScheduleList', description: '查询关键词监控任务执行批次', cost: '0 request' },
  'keyword-batch-schedule-detail': { title: 'KeywordBatchScheduleDetail', description: '提取关键词监控产品列表详细数据', cost: '0 request' },
  'best-seller-list-subscription': { title: 'BestSellerListSubscription', description: '榜单监控任务注册', cost: '0 request' },
  'best-seller-list-task': { title: 'BestSellerListTask', description: '榜单监控任务查询', cost: '0 request' },
  'best-seller-list-delete': { title: 'BestSellerListDelete', description: '榜单监控任务删除', cost: '0 request' },
  'best-seller-list-data-collect': { title: 'BestSellerListDataCollect', description: '榜单监控数据提取', cost: '0 request' },
  'product-seller-subscription': { title: 'ProductSellerSubscription', description: '跟卖&库存监控', cost: '0 request' },
  'product-seller-tasks': { title: 'ProductSellerTasks', description: '跟卖&库存监控任务查询', cost: '0 request' },
  'product-seller-task-update': { title: 'ProductSellerTaskUpdate', description: '修改跟卖&库存监控任务', cost: '0 request' },
  'product-seller-task-schedule-list': { title: 'ProductSellerTaskScheduleList', description: '查询跟卖&库存监控任务执行批次', cost: '0 request' },
  'product-seller-task-schedule-detail': { title: 'ProductSellerTaskScheduleDetail', description: '提取跟卖&库存监控执行结果详细数据', cost: '0 request' },
  'asin-subscription': { title: 'ASINSubscription', description: 'ASIN更新订阅', cost: '0 request' },
  'asin-subscription-query': { title: 'ASINSubscriptionQuery', description: 'ASIN订阅查询', cost: '0 request' },
  'asin-subscription-collection': { title: 'ASINSubscriptionCollection', description: 'ASIN订阅结果数据查询', cost: '0 request' },
  'coin-query': { title: 'CoinQuery', description: '本月剩余积分查询', cost: '1 request' },
  'coin-stream': { title: 'CoinStream', description: '积分使用明细查询', cost: '1 request' },
  'request-stream': { title: 'RequestStream', description: '月度Request使用明细查询', cost: '1 request' }
}

const currentDoc = computed(() => apiDocs[activeEndpoint.value])

// Computed Payload for Preview & Sending
const requestPayload = computed(() => {
  const base = { domain: form.domain }
  
  switch (activeEndpoint.value) {
    case 'product':
      return {
        ...base,
        ASIN: form.asins.split(/[\n,]/).map(s => s.trim()).filter(s => s).join(','),
        Trend: 1
      }
    case 'category':
      return { ...base, nodeId: form.nodeId }
    case 'category-tree':
      return { ...base }
    case 'category-trend':
      return { ...base, nodeId: form.nodeId, trendIndex: form.trendIndex }
    case 'category-products':
      return { ...base, nodeId: form.nodeId, page: form.page }
    case 'product-query':
      return {
        ...base,
        query: 1, // Default to single condition for simplicity
        queryType: form.queryType,
        pattern: form.pattern,
        page: form.page
      }
    case 'keyword-query':
      return { ...base, pattern: { keyword: form.keyword }, pageIndex: form.page }
    case 'keyword-detail':
      return { ...base, keyword: form.keyword }
    case 'keyword-search-results':
      return { ...base, keyword: form.keyword, pageIndex: form.page }
    case 'asin-sales-volume':
      return { ...base, asin: form.asins.trim(), queryDate: form.queryStart, queryEndDate: form.queryEnd, page: form.page }
    case 'product-variation-history':
      return { ...base, asin: form.asins.trim() }
    case 'product-trend':
      return { 
        ...base, 
        asin: form.asins.trim(), 
        dateRange: form.queryStart && form.queryEnd ? `${form.queryStart},${form.queryEnd}` : '',
        trendType: form.trendIndex 
      }
    case 'product-realtime':
      return { ...base, asin: form.asins.trim(), update: form.update }
    case 'product-realtime-status':
      return { ...base, queryDate: form.queryStart } // Using queryStart as queryDate
    case 'reviews-collection':
      return { 
        ...base, 
        asin: form.asins.trim(), 
        mode: form.mode, 
        star: form.star, 
        onlyPurchase: form.onlyPurchase, 
        page: form.page 
      }
    case 'reviews-collection-status':
      return { ...base, asin: form.asins.trim(), update: form.update }
    case 'reviews-query':
      return { 
        ...base, 
        asin: form.asins.trim(), 
        querystartdt: form.queryStart, 
        star: form.star, // Simplified, assumes single int or string
        onlyPurchase: form.onlyPurchase, 
        pageIndex: form.page 
      }
    case 'similar-product-realtime':
      return { ...base, image: form.image }
    case 'similar-product-status':
      return { ...base, Update: form.update }
    case 'similar-product-result':
      return { ...base, taskId: form.taskId }
    case 'keyword-search-result-trend':
      return { ...base, keyword: form.keyword, pageIndex: form.page }
    case 'category-request-keyword':
      return { ...base, nodeId: form.nodeId, pageIndex: form.page }
    case 'asin-request-keyword':
      return { ...base, asin: form.asins.trim(), pageIndex: form.page }
    case 'keyword-product-ranking':
      return { ...base, keyword: form.keyword, pageIndex: form.page }
    case 'asin-keyword-ranking':
      return { ...base, keyword: form.keyword, asin: form.asins.trim(), queryStart: form.queryStart, queryEnd: form.queryEnd, page: form.page }
    case 'keyword-subscription':
    case 'best-seller-list-subscription':
    case 'product-seller-subscription':
    case 'asin-subscription':
      // Complex subscription payload, using 'asins' or 'keyword' as placeholder for raw input or simplified
      return { ...base, content: form.asins } 
    case 'keyword-tasks':
    case 'best-seller-list-task':
    case 'product-seller-tasks':
    case 'asin-subscription-query':
      return { ...base, pageIndex: form.page }
    case 'keyword-task-update':
    case 'product-seller-task-update':
      return { ...base, taskId: form.taskId, update: form.update }
    case 'keyword-batch-schedule-list':
    case 'product-seller-task-schedule-list':
      return { ...base, taskId: form.taskId }
    case 'keyword-batch-schedule-detail':
    case 'product-seller-task-schedule-detail':
      return { ...base, scheduleId: form.taskId } // Reusing taskId as scheduleId
    case 'best-seller-list-delete':
      return { ...base, taskId: form.taskId }
    case 'best-seller-list-data-collect':
      return { ...base, taskId: form.taskId, queryDate: form.queryStart }
    case 'asin-subscription-collection':
      return { ...base, asins: form.asins }
    case 'coin-query':
      return { ...base }
    case 'coin-stream':
    case 'request-stream':
      return { ...base, platform: 0, pageIndex: form.page } // Default platform 0
    default:
      return {}
  }
})

// Extract images for preview (Legacy, kept for reference but UI moved to Visual Tab)
// Commented out to avoid unused variable warning
// const previewImages = computed(() => {
//   if (!response.value) return []
//   const imgs: string[] = []
//   
//   // eslint-disable-next-line @typescript-eslint/no-explicit-any
//   const extract = (obj: any) => {
//     if (!obj) return
//     if (obj.Photo && Array.isArray(obj.Photo)) imgs.push(...obj.Photo)
//     if (obj.EBCPhoto && Array.isArray(obj.EBCPhoto)) imgs.push(...obj.EBCPhoto)
//     if (obj.Data) extract(obj.Data)
//     if (Array.isArray(obj)) obj.forEach(extract)
//   }
//   
//   extract(response.value)
//   return imgs.slice(0, 10)
// })

// Helper: Extract Product Data from Response
// Helper: Extract Product Data from Response (Normalized to Array)
const productData = computed(() => {
  if (!response.value || activeEndpoint.value !== 'product') return []
  
  const data = response.value.data || response.value
  
  // If data is null/undefined
  if (!data) return []
  
  // If single object, wrap in array
  if (!Array.isArray(data)) {
    return [data]
  }
  
  return data
})

// Helper: Check if trend data exists
// Commented out to avoid unused variable warning
// const hasTrendData = (key: string) => {
//   if (!productData.value || !productData.value.length) return false
//   const product = productData.value[0]
//   return product && 
//          product[key] && 
//          Array.isArray(product[key]) && 
//          product[key].length > 0
// }

// Helper: Format Price
const formatPrice = (price: number, domain: number) => {
  // Simple heuristic: most domains use cents/minor units. 
  // Domain 7 (JP) usually uses Yen (no decimals).
  if (domain === 7) return `¥${price}`
  return `$${(price / 100).toFixed(2)}`
}

// Helper: Parse Property (Specifications)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const parseProperty = (prop: any): { key: string, value?: string }[] => {
  if (!prop) return []
  
  let items: string[] = []
  
  if (Array.isArray(prop)) {
    items = prop
  } else if (typeof prop === 'string') {
    try {
      const parsed = JSON.parse(prop)
      if (Array.isArray(parsed)) items = parsed
      else items = [prop]
    } catch (e) {
      items = [prop]
    }
  }
  
  // Strategy: Identify if the array is a flat list of [Key, Value, Key, Value]
  // We check if "even" indexed items are common Keys
  const commonKeys = new Set([
    'Brand', 'Color', 'Material', 'Item Weight', 'Item Dimensions', 'Product Dimensions',
    'Manufacturer', 'Included Components', 'Style', 'Pattern', 'Shape',
    'Power Source', 'Voltage', 'Wattage', 'Unit Count', 'Size', 'Compatible Devices',
    'Capacity', 'Configuration', 'Special Feature', 'Installation Type', 'Number of Doors',
    'Defrost System', 'Finish Type', 'Form Factor', 'Lock Type', 'Control Method',
    'Noise Level', 'Mounting Type', 'Part Number', 'Item Model Number'
  ])
  
  // Check if it looks like a Key-Value pairs list
  // Heuristic: If even items contain known keys, it's likely a pair list.
  // We lower the threshold and check specific strong signals.
  let keyMatchCount = 0
  let hasStrongSignal = false // If we see "Brand" or "Manufacturer" at even index, it's a strong signal
  
  for (let i = 0; i < items.length; i += 2) {
    const str = String(items[i]).trim()
    if (commonKeys.has(str)) {
      keyMatchCount++
      if (str === 'Brand' || str === 'Manufacturer' || str === 'Product Dimensions') {
        hasStrongSignal = true
      }
    }
  }
  
  // If we have a strong signal, we trust it's a pair list.
  // Otherwise, we require a small percentage of matches (15%).
  const isFlatPairs = items.length > 1 && items.length % 2 === 0 && (
    hasStrongSignal || 
    (keyMatchCount / (items.length / 2)) >= 0.15
  )
  
  if (isFlatPairs) {
    const result = []
    for (let i = 0; i < items.length; i += 2) {
      const key = String(items[i]).trim()
      const val = items[i+1] ? String(items[i+1]).trim() : ''
      result.push({ key: key, value: val })
    }
    return result
  }
  
  // Post-process items to try and separate Key/Value if they are combined strings
  // Note: Sorftime API often returns Property as just keys or "Key: Value" strings.
  return items.map(item => {
    if (typeof item !== 'string') return { key: String(item) }
    
    // Try to split by first colon if it looks like a key-value pair
    // e.g. "Material: Plastic"
    const parts = item.split(':')
    if (parts.length > 1) {
      return {
        key: (parts[0] || '').trim(),
        value: parts.slice(1).join(':').trim()
      }
    }
    
    return { key: item }
  })
}

// Helper: Translation Dictionary (Expanded)
const translationDict: Record<string, string> = {
  // Colors
  'Black': '黑色', 'White': '白色', 'Blue': '蓝色', 'Red': '红色', 'Green': '绿色',
  'Yellow': '黄色', 'Pink': '粉色', 'Purple': '紫色', 'Grey': '灰色', 'Gray': '灰色',
  'Silver': '银色', 'Gold': '金色', 'Rose Gold': '玫瑰金', 'Multicolor': '多彩',
  'Transparent': '透明', 'Clear': '透明', 'Beige': '米色', 'Brown': '棕色',
  
  // Materials
  'Plastic': '塑料', 'Metal': '金属', 'Glass': '玻璃', 'Wood': '木头',
  'Leather': '皮革', 'Silicone': '硅胶', 'Rubber': '橡胶', 'Ceramic': '陶瓷',
  'Stainless Steel': '不锈钢', 'Aluminum': '铝合金', 'Cotton': '棉',
  'Polyester': '涤纶', 'Nylon': '尼龙', 'Polycarbonate': '聚碳酸酯',
  'Acrylonitrile Butadiene Styrene': 'ABS树脂', 'Canvas': '帆布',
  
  // Features / Adjectives
  'Wireless': '无线', 'Portable': '便携', 'Waterproof': '防水', 'Lightweight': '轻量',
  'Rechargeable': '可充电', 'Bluetooth': '蓝牙', 'Adjustable': '可调节',
  'Durable': '耐用', 'Compact': '紧凑', 'Foldable': '可折叠',
  'Heavy Duty': '重型', 'Non-slip': '防滑', 'Cordless': '无绳',
  'Digital': '数字', 'Analog': '模拟', 'Automatic': '自动',
  
  // Units / Dimensions
  'Inch': '英寸', 'Inches': '英寸', 'cm': '厘米', 'mm': '毫米',
  'kg': '千克', 'g': '克', 'lb': '磅', 'oz': '盎司',
  'Volt': '伏特', 'Watt': '瓦特', 'mAh': '毫安时',
  
  // Common Keys (Fallback if value is missing)
  'Brand': '品牌', 'Color': '颜色', 'Material': '材质',
  'Item Weight': '重量', 'Item Dimensions': '尺寸',
  'Manufacturer': '制造商', 'Included Components': '组件',
  'Style': '风格', 'Pattern': '图案', 'Shape': '形状',
  'Power Source': '电源', 'Voltage': '电压', 'Wattage': '瓦数',
  'Unit Count': '单位数量'
}

const getTranslation = (text: string) => {
  if (!text) return ''
  const cleanText = text.trim()
  
  // Direct match (Case insensitive)
  const lowerText = cleanText.toLowerCase()
  for (const [key, val] of Object.entries(translationDict)) {
    if (key.toLowerCase() === lowerText) return val
  }
  
  // Partial match for common terms
  for (const [key, val] of Object.entries(translationDict)) {
    // Use word boundary to avoid partial replacements like "Kilograms" -> "Kilo克rams"
    // Escape special regex chars in key just in case
    const escapedKey = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`\\b${escapedKey}\\b`, 'gi');
    if (regex.test(cleanText)) {
      return cleanText.replace(regex, val)
    }
  }
  
  return '' // Return empty if no translation found to keep UI clean
}

// Helper: Parse Trend Array [date, val, date, val...] -> [[date, val], ...]
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const parseTrendData = (flatArray: any[]) => {
  const data = []
  for (let i = 0; i < flatArray.length; i += 2) {
    const dateStr = String(flatArray[i])
    // Format date: 20251202 -> 2025-12-02
    const date = `${dateStr.slice(0, 4)}-${dateStr.slice(4, 6)}-${dateStr.slice(6, 8)}`
    const val = flatArray[i+1]
    if (val !== -1) { // Filter out invalid data
      data.push([date, val])
    }
  }
  return data
}

// Render Charts
const renderCharts = () => {
  if (!productData.value || productData.value.length === 0) return
  
  // For charts, we currently only visualize the first product in the list
  // In a future update, we could allow selecting which product to visualize
  const targetProduct = productData.value[0]
  
  // Helper to check trend data on a specific product object
  const hasTrend = (key: string) => {
    return targetProduct && 
           targetProduct[key] && 
           Array.isArray(targetProduct[key]) && 
           targetProduct[key].length > 0
  }

  // Sales Chart
  if (salesChartRef.value && hasTrend('ListingSalesVolumeOfDailyTrend')) {
    if (salesChart) salesChart.dispose()
    salesChart = echarts.init(salesChartRef.value)
    const data = parseTrendData(targetProduct.ListingSalesVolumeOfDailyTrend)
    
    salesChart.setOption({
      title: { text: 'Daily Sales Trend', left: 'center', textStyle: { fontSize: 14 } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'time' },
      yAxis: { type: 'value', name: 'Sales' },
      series: [{
        data: data,
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.1 },
        itemStyle: { color: '#3b82f6' }
      }],
      grid: { top: 40, right: 20, bottom: 20, left: 50, containLabel: true }
    })
  }

  // Price Chart
  if (priceChartRef.value && hasTrend('PriceTrend')) {
    if (priceChart) priceChart.dispose()
    priceChart = echarts.init(priceChartRef.value)
    const data = parseTrendData(targetProduct.PriceTrend)
    // Adjust price values (cents -> dollars)
    const formattedData = data.map(item => [item[0], item[1] / 100])
    
    priceChart.setOption({
      title: { text: 'Price Trend', left: 'center', textStyle: { fontSize: 14 } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'time' },
      yAxis: { type: 'value', name: 'Price', axisLabel: { formatter: '${value}' } },
      series: [{
        data: formattedData,
        type: 'step', // Price usually changes in steps
        itemStyle: { color: '#10b981' }
      }],
      grid: { top: 40, right: 20, bottom: 20, left: 50, containLabel: true }
    })
  }
}

// Watch for response/view mode changes to render charts
watch([response, responseViewMode], async () => {
  if (response.value && responseViewMode.value === 'visual' && activeEndpoint.value === 'product') {
    await nextTick()
    renderCharts()
  }
})

// Resize charts on window resize
const handleResize = () => {
  salesChart?.resize()
  priceChart?.resize()
}
window.addEventListener('resize', handleResize)
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  salesChart?.dispose()
  priceChart?.dispose()
})

// API Setup
const getBaseUrl = () => {
  // Fix: Cast import.meta to any to avoid TS error if types aren't set up
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const url = (import.meta as any).env.VITE_API_BASE_URL || '/api/v1'
  if (url.endsWith('/api/v1')) return url
  return url.replace(/\/$/, '') + '/api/v1'
}

const api = axios.create({
  baseURL: getBaseUrl()
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Computed Business Status
const businessStatus = computed(() => {
  if (!response.value) return null
  
  // Handle both PascalCase (API) and camelCase (Pydantic) keys
  const code = response.value.Code ?? response.value.code
  const msg = response.value.Message ?? response.value.message
  
  // Sorftime Error Codes Mapping
  const errorMap: Record<number, string> = {
    0: 'Success',
    9: 'Access Restricted',
    10: 'Parameter Error',
    400: 'Unauthorized IP',
    401: 'Interface Not Open',
    402: 'No Permission',
    500: 'Monthly Limit Reached',
    501: 'Minute Limit Reached',
    694: 'Insufficient Request Quota (余额不足)'
  }
  
  const desc = errorMap[code] || msg || 'Unknown Status'
  
  return {
    code,
    text: desc,
    isError: code !== 0
  }
})

const jsonViewOptions = reactive({
  compact: false,
  wrap: true,
  selectedKeys: [] as string[]
})

const availableKeys = computed(() => {
  if (!response.value) return []
  // If response has data wrapper, use that for keys if it's an object
  const target = response.value.data || response.value
  if (typeof target === 'object' && target !== null && !Array.isArray(target)) {
    return Object.keys(target)
  }
  return Object.keys(response.value)
})

const filteredResponse = computed(() => {
  if (!response.value) return null
  
  // If no keys selected, return full response
  if (jsonViewOptions.selectedKeys.length === 0) {
    return response.value
  }
  
  // If filtering, we likely want to filter the 'data' object if it exists
  // But to keep structure valid, we should probably return the full structure 
  // but with only selected keys in the data part, OR just the selected keys if they are top level.
  // Let's assume user wants to filter the MAIN content.
  
  const target = response.value.data || response.value
  
  if (typeof target === 'object' && target !== null && !Array.isArray(target)) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const filtered: any = {}
    jsonViewOptions.selectedKeys.forEach(key => {
      if (key in target) {
        filtered[key] = target[key]
      }
    })
    
    // If we filtered the inner data, wrap it back if needed, or just return the filtered object
    // Returning just the filtered object is cleaner for "viewing specific fields"
    return filtered
  }
  
  return response.value
})

// Actions
const handleSend = async () => {
  loading.value = true
  response.value = null
  error.value = null
  responseStatus.value = null
  const startTime = Date.now()

  try {
    const res = await api.post(`/sorftime/test/${activeEndpoint.value}`, requestPayload.value)
    
    response.value = res.data
    responseStatus.value = {
      code: res.status,
      text: res.statusText,
      time: Date.now() - startTime
    }
    // Switch to visual view if product endpoint and data is available
    if (activeEndpoint.value === 'product' && productData.value) {
      responseViewMode.value = 'visual'
    } else {
      responseViewMode.value = 'json'
    }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } catch (err: any) {
    console.error(err)
    error.value = err.response?.data || err.message
    responseStatus.value = {
      code: err.response?.status || 0,
      text: err.response?.statusText || 'Error',
      time: Date.now() - startTime
    }
    responseViewMode.value = 'json' // Always show JSON on error
  } finally {
    loading.value = false
  }
}

const copyResponse = () => {
  if (response.value) {
    navigator.clipboard.writeText(JSON.stringify(response.value, null, 2))
    ElMessage.success('Response copied to clipboard')
  }
}

// Simple JSON Syntax Highlighter
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const highlightJson = (json: any) => {
  if (typeof json !== 'string') {
    json = JSON.stringify(json, null, 2)
  }
  json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  // eslint-disable-next-line no-useless-escape
  return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match: string) => {
    let cls = 'number'
    if (/^"/.test(match)) {
      if (/:$/.test(match)) {
        cls = 'key'
      } else {
        cls = 'string'
      }
    } else if (/true|false/.test(match)) {
      cls = 'boolean'
    } else if (/null/.test(match)) {
      cls = 'null'
    }
    return `<span class="${cls}">${match}</span>`
  })
}
</script>

<style scoped lang="scss">
.postman-container {
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  background-color: #f3f4f6;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.request-bar {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  gap: 12px;
}

.method-badge {
  font-weight: bold;
}

.url-input {
  flex: 1;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: row; // Ensure row layout
  overflow: hidden;
}

.pane {
  display: flex;
  flex-direction: column;
  background: #fff;
  overflow: hidden;
  
  &.request-pane {
    flex: 3; // 30% width
    min-width: 320px;
    border-right: 1px solid #e5e7eb;
    display: flex;
    flex-direction: column;
    
    .sidebar-header {
      padding: 16px;
      border-bottom: 1px solid #e5e7eb;
      background: #fff;
      
      .endpoint-selector {
        margin-bottom: 12px;
        display: flex;
        gap: 8px;
        
        .method-tag {
          height: 32px;
          line-height: 30px;
        }
        
        .endpoint-select {
          flex: 1;
        }
      }
      
      .send-btn {
        width: 100%;
        height: 40px;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.5px;
      }
    }

    .sidebar-content {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      
      .sidebar-section {
        margin-bottom: 24px;
        
        &.info-section {
          background: #f9fafb;
          padding: 12px;
          border-radius: 6px;
          border: 1px solid #e5e7eb;
          
          .doc-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            
            .doc-title {
              font-weight: 600;
              color: #374151;
              font-size: 0.9rem;
            }
          }
          
          .doc-desc {
            font-size: 0.8rem;
            color: #6b7280;
            margin: 0 0 8px 0;
            line-height: 1.4;
          }
          
          .doc-note {
            display: flex;
            gap: 6px;
            align-items: flex-start;
            font-size: 0.75rem;
            color: #d97706;
            background: #fffbeb;
            padding: 6px;
            border-radius: 4px;
            
            .el-icon {
              margin-top: 2px;
            }
          }
        }
        
        &.params-section {
          .section-header {
            font-size: 0.85rem;
            text-transform: uppercase;
            color: #9ca3af;
            margin: 0 0 16px 0;
            font-weight: 600;
            letter-spacing: 0.5px;
          }
          
          .param-group {
            margin-bottom: 16px;
            
            label {
              display: block;
              font-size: 0.85rem;
              font-weight: 500;
              color: #374151;
              margin-bottom: 6px;
            }
            
            .param-tip {
              margin-top: 4px;
              font-size: 0.75rem;
              color: #9ca3af;
            }
          }
          
          .empty-param {
            margin-top: 8px;
          }
        }
      }
    }
  }
  
  &.response-pane {
    flex: 7; // 70% width
    min-width: 0;
  }
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
  
  .endpoint-selector {
    margin-bottom: 12px;
    display: flex;
    gap: 8px;
    
    .method-tag {
      height: 32px;
      line-height: 30px;
    }
    
    .endpoint-select {
      flex: 1;
    }
  }
  
  .send-btn {
    width: 100%;
    height: 40px;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.5px;
  }
}

.pane-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
  
  .endpoint-selector {
    margin-bottom: 12px;
    display: flex;
    gap: 8px;
    
    .method-tag {
      height: 32px;
      line-height: 30px;
    }
    
    .endpoint-select {
      flex: 1;
    }
  }
  
  .send-btn {
    width: 100%;
    height: 40px; // Large button
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.5px;
  }
}

.pane-header {
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  padding: 0 12px;
  height: 40px;
  display: flex;
  align-items: center;
  
  &.response-header {
    justify-content: space-between;
  }
}

.custom-tabs {
  width: 100%;
  
  :deep(.el-tabs__header) {
    margin-bottom: 0;
  }
  
  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
  }
}

.tab-label {
  font-size: 0.9rem;
  color: #606266;
  font-weight: 500;
}

.status-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pane-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  position: relative;
}

// API Info Card
.api-info-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 24px;
  
  .api-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    
    .api-title {
      margin: 0;
      font-size: 1.1rem;
      color: #303133;
    }
  }
  
  .api-desc {
    color: #606266;
    font-size: 0.9rem;
    margin: 0 0 12px 0;
  }
  
  .api-note {
    margin-top: 12px;
  }
}

// Param Row Layout
.param-row {
  display: flex;
  flex-direction: column; // Always stack vertically in narrow pane
  gap: 12px;
  margin-bottom: 24px;
  border-bottom: 1px solid #f0f2f5;
  padding-bottom: 24px;
  
  &:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
  
  .param-input {
    width: 100%;
  }
  
  .param-doc {
    width: 100%;
    background: #fdf6ec;
    padding: 12px;
    border-radius: 4px;
    border-left: 4px solid #e6a23c;
    
    .doc-title {
      font-family: monospace;
      font-weight: bold;
      color: #303133;
      margin-bottom: 4px;
    }
    
    .doc-desc {
      font-size: 0.85rem;
      color: #606266;
      line-height: 1.5;
      
      &.text-red {
        color: #f56c6c;
      }
    }
  }
}

// Form Styles
.form-section {
  margin-bottom: 32px;
  
  .section-title {
    font-size: 0.8rem;
    text-transform: uppercase;
    color: #909399;
    font-weight: 700;
    margin-bottom: 12px;
    letter-spacing: 0.05em;
  }
}

.form-row {
  margin-bottom: 16px;
  
  label {
    display: block;
    font-size: 0.85rem;
    font-weight: 600;
    color: #606266;
    margin-bottom: 6px;
  }
  
  .help-text {
    font-size: 0.75rem;
    color: #909399;
    margin-top: 4px;
  }
}

// JSON Toolbar
.json-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  background: #f5f7fa;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  
  .toolbar-actions {
    display: flex;
    gap: 12px;
  }
}

// Code Viewer
.code-viewer-container {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  height: 100%;
  overflow: auto;
  
  &.is-compact {
    .code-viewer {
      font-size: 0.75rem;
      line-height: 1.2;
    }
  }
  
  &.is-wrap {
    .code-viewer {
      white-space: pre-wrap;
      word-break: break-all;
    }
  }
}

.code-viewer {
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 0.85rem;
  line-height: 1.5;
  margin: 0;
}

.response-viewer {
  background: #ffffff;
  border: none;
  padding: 0;
}

// Detail View Styles
.detail-view {
  height: 100%;
  overflow-y: auto;
  padding-right: 8px;
  
  .detail-header {
    display: flex;
    gap: 24px;
    margin-bottom: 32px;
    background: #fff;
    padding: 24px;
    border-radius: 8px;
    border: 1px solid #e4e7ed;
    
    .detail-img-box {
      width: 200px;
      height: 200px;
      border: 1px solid #f0f2f5;
      border-radius: 8px;
      overflow: hidden;
      flex-shrink: 0;
      
      .detail-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
      }
      
      .img-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f5f7fa;
        color: #909399;
      }
    }
    
    .detail-info {
      flex: 1;
      
      .detail-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #303133;
        margin: 0 0 16px 0;
        line-height: 1.4;
      }
      
      .detail-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
        
        .detail-price {
          font-size: 1.5rem;
          font-weight: bold;
          color: #f56c6c;
          margin-left: auto;
        }
      }
      
      .detail-metrics {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
        
        .metric-card {
          background: #f9fafb;
          padding: 16px;
          border-radius: 8px;
          text-align: center;
          
          .metric-label {
            font-size: 0.8rem;
            color: #909399;
            text-transform: uppercase;
            margin-bottom: 8px;
          }
          
          .metric-value {
            font-size: 1.2rem;
            font-weight: 600;
            color: #303133;
            
            &.text-green { color: #67c23a; }
            &.text-orange { color: #e6a23c; }
          }
          
          .metric-sub {
            font-size: 0.75rem;
            color: #909399;
            margin-top: 4px;
          }
        }
      }

      .header-specs {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding-top: 16px;
        border-top: 1px solid #f0f2f5;
        
        .spec-tag {
          background: #ecf5ff;
          border: 1px solid #d9ecff;
          padding: 6px 12px;
          border-radius: 4px;
          display: flex;
          flex-direction: column;
          gap: 2px;
          
          .spec-main {
            font-size: 0.85rem;
            font-weight: 600;
            color: #409eff;
          }
          
          .spec-trans {
            font-size: 0.75rem;
            color: #909399;
          }
        }
      }
    }
  }
  
  .detail-content {
    .info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 32px;
      margin-bottom: 32px;
      
      @media (max-width: 1200px) {
        grid-template-columns: 1fr;
      }
    }
    
    .detail-section {
      margin-bottom: 32px;
      
      h3 {
        font-size: 1.1rem;
        color: #303133;
        margin: 0 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #ebeef5;
      }
      
      .feature-list-lg {
        padding-left: 20px;
        line-height: 1.6;
        color: #606266;
        
        li {
          margin-bottom: 8px;
        }
      }
      
      .desc-text {
        font-size: 0.9rem;
        line-height: 1.6;
        color: #606266;
        white-space: pre-wrap;
        max-height: 300px;
        overflow-y: auto;
        background: #f9fafb;
        padding: 16px;
        border-radius: 4px;
      }
      
      .specs-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        
        .spec-item {
          background: #f0f2f5;
          padding: 8px 16px;
          border-radius: 4px;
          font-size: 0.85rem;
          color: #606266;
          border: 1px solid #e4e7ed;
          display: flex;
          flex-direction: column;
          gap: 2px;
          
          .spec-main {
            font-weight: 600;
            color: #303133;
          }
          
          .spec-trans {
            font-size: 0.75rem;
            color: #909399;
          }
        }
      }
    }
  }
}

// Comparison Table Styles
.comparison-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .product-cell {
    display: flex;
    gap: 12px;
    align-items: center;
    
    .product-img {
      width: 60px;
      height: 60px;
      flex-shrink: 0;
      border: 1px solid #eee;
      border-radius: 4px;
      overflow: hidden;
      
      .main-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
      }
      
      .img-placeholder {
        width: 100%;
        height: 100%;
        background: #f5f7fa;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        color: #909399;
      }
    }
    
    .product-details {
      flex: 1;
      min-width: 0;
      
      .product-title {
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      
      .product-meta {
        display: flex;
        gap: 8px;
        align-items: center;
        
        .brand {
          font-size: 0.75rem;
          color: #909399;
        }
      }
    }
  }
  
  .price-text {
    font-weight: bold;
    color: #f56c6c;
  }
  
  .feature-list {
    margin: 0;
    padding-left: 20px;
    font-size: 0.85rem;
    line-height: 1.4;
    
    li {
      margin-bottom: 4px;
    }
  }
  
  .specs-list {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
  
  .charts-section {
    margin-top: 20px;
    border-top: 1px solid #ebeef5;
    padding-top: 20px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    flex-shrink: 0;
    
    .chart-wrapper {
      height: 300px;
      background: #f9fafb;
      border-radius: 8px;
      padding: 12px;
      
      .echart-instance {
        width: 100%;
        height: 100%;
      }
    }
  }
}

.text-gray {
  color: #909399;
  font-style: italic;
  font-size: 0.8rem;
}

// JSON Syntax Highlighting
:deep(.key) { color: #795da3; }
:deep(.string) { color: #183691; }
:deep(.number) { color: #0086b3; }
:deep(.boolean) { color: #0086b3; }
:deep(.null) { color: #0086b3; }

// States
.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  
  .spinner {
    width: 30px;
    height: 30px;
    border: 3px solid #e5e7eb;
    border-top-color: #409eff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// Responsive
@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .pane.request-pane {
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    height: 50%;
  }
  
  .param-row {
    flex-direction: column;
    gap: 12px;
    
    .param-input {
      min-width: 100%;
    }
  }
  
  .charts-container {
    grid-template-columns: 1fr;
  }
}
</style>
```
