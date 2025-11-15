<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>Sorftime 控制台登录</h2>
      <el-form>
        <el-form-item label="账号">
          <el-input placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-button type="primary" block>登录（占位）</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f0f2f5;
}

.login-card {
  width: 360px;
}
</style>
