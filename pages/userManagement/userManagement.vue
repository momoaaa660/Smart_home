<template>
  <view class="container">
    <image src="@/static/img/home_bg.png" class="bg"></image>
    <view class="overlay"></view>

    <view class="content">
      <view class="card">
        <view v-for="(user, index) in users" :key="index" class="user-item">
          <view>
            <text class="username">{{ user.username }}</text>
            <text class="time">注册时间：{{ user.registerTime }}</text>
          </view>
          <button class="btn-del" @click="deleteUser(user)">删除</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() { return { users: [] } },
  onShow() { this.users = uni.getStorageSync("users") || [] },
  methods: {
    deleteUser(user) {
      const current = uni.getStorageSync("currentUser")
      if (current && current.username === user.username) {
        uni.showToast({ title: "不能删除当前登录用户", icon: "none" })
        return
      }
      this.users = this.users.filter(u => u.username !== user.username)
      uni.setStorageSync("users", this.users)
      uni.showToast({ title: "删除成功", icon: "success" })
    }
  }
}
</script>

<style scoped lang="scss">
.container { position: relative; width: 100%; height: 100vh; }
.bg { position: absolute; width: 100%; height: 100%; object-fit: cover; }
.overlay { position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.3); }
.content { position: relative; z-index: 2; padding: 30rpx; }
.card { background: rgba(255,255,255,0.95); border-radius: 20rpx; padding: 20rpx; }
.user-item { display: flex; justify-content: space-between; align-items: center; padding: 20rpx 0; border-bottom: 1rpx solid #eee; }
.username { font-size: 30rpx; font-weight: bold; margin-right: 10rpx; }
.time { font-size: 24rpx; color: #666; display: block; }
.btn-del { background: #ff4d4f; color: #fff; padding: 10rpx 20rpx; border-radius: 20rpx; font-size: 26rpx; }
</style>


