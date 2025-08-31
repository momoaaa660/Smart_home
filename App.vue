<script>
import store from "./store/index.js"
export default {
  onLaunch() {
    console.log("App Launch")
    // 检查登录
    if (!store.getters.isLoggedIn) {
      uni.reLaunch({
        url: "/pages/login/login"
      })
    }
  },
  onShow() {
    console.log("App Show")
  },
  onHide() {
    console.log("App Hide")
  }
}
</script>

<style lang="scss">
@import "uview-ui/index.scss";
body,
html,
page {
  padding: 0;
  margin: 0;
  height: 100%;
}
</style>

