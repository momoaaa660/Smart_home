<template>
  <view class="container">
    <image src="@/static/img/home_bg.png" class="bg"></image>
    <view class="overlay"></view>

    <view class="content">
      <!-- 用户信息 -->
      <view class="userinfo-card">
        <view class="user-info-row">
          <text class="username">{{ username }}</text>
          <text class="status">{{ isLogin ? "已登录" : "未登录" }}</text>
        </view>
      </view>

      <!-- 功能菜单 -->
      <view class="menu-card">
        <view class="menu-item" @click="goUserManagement">
          <image src="@/static/icon/friend.png" class="icon-img"/>
          <text class="menu-text">用户管理</text>
        </view>

        <view class="menu-item" @click="goChangePassword">
          <image src="@/static/icon/device_active.png" class="icon-img"/>
          <text class="menu-text">修改密码</text>
        </view>

        <view class="menu-item" @click="logout">
          <image src="@/static/icon/out.png" class="icon-img"/>
          <text class="menu-text">退出登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return { isLogin: false, username: "游客" }
  },
  onShow() {
    const loginStatus = uni.getStorageSync("isLogin") || false
    const currentUser = uni.getStorageSync("currentUser") || {}
    this.isLogin = loginStatus
    this.username = loginStatus && currentUser.username ? currentUser.username : "游客"
  },
  methods: {
    goUserManagement() { uni.navigateTo({ url: "/pages/userManagement/userManagement" }) },
    goChangePassword() { uni.navigateTo({ url: "/pages/changePassword/changePassword" }) },
    logout() {
      uni.showModal({
        title: "退出登录", content: "确定要退出登录吗？",
        success: (res) => {
          if (res.confirm) {
            uni.removeStorageSync("isLogin")
            uni.removeStorageSync("currentUser")
            this.isLogin = false
            this.username = "游客"
            uni.reLaunch({ url: "/pages/login/login" })
          }
        }
      })
    }
  }
}
</script>

<style scoped lang="scss">
.container { position: relative; width: 100%; height: 100vh; }
.bg { position: absolute; width: 100%; height: 100%; object-fit: cover; }
.overlay { position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.25); }
.content { position: relative; z-index: 2; display: flex; flex-direction: column; padding: 50rpx 20rpx; }
.userinfo-card {
  width: 90%; background: rgba(255,255,255,0.95); border-radius: 20rpx; padding: 30rpx; margin-bottom: 30rpx;
  .user-info-row { display: flex; align-items: center;
    .username { font-size: 32rpx; font-weight: bold; margin-right: 20rpx; }
    .status { font-size: 26rpx; color: #38f9d7; }
  }
}
.menu-card { width: 90%; background: rgba(255,255,255,0.95); border-radius: 20rpx; box-shadow: 0 8rpx 20rpx rgba(0,0,0,0.15);
  display: flex; flex-direction: column; padding: 20rpx; }
.menu-item { display: flex; align-items: center; padding: 20rpx 0; border-bottom: 1rpx solid #eee; }
.icon-img { width: 40rpx; height: 40rpx; margin-right: 20rpx; }
.menu-text { font-size: 28rpx; color: #333; }
</style>
