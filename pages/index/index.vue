<template>
  <view class="page-container">
    <!-- 带背景的页面（确保背景图正确显示） -->
    <view class="page" :style="{ 
      backgroundImage: 'url(/static/img/home_bg.png)', 
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundAttachment: 'fixed'
    }">
      <!-- 顶部标题 -->
      <view class="header">
        <text class="title">CQU Home</text>
      </view>

      <!-- 场景导航 -->
      <scroll-view scroll-x class="scene-nav">
        <view 
          v-for="item in scenes" 
          :key="item" 
          :class="['scene-item', currentScene === item ? 'active' : '']"
          @click="changeScene(item)">
          {{ item }}
        </view>
      </scroll-view>

      <!-- 环境监测测区：紧凑布局，向左并拢 -->
      <view class="status-container">
        <!-- 时间卡片 -->
        <view class="status-card">
          <image src="/static/icon/time.png" class="status-icon" />
          <text class="status-value">{{ currentTime }}</text>
        </view>
        
        <!-- 温度卡片（显示整数数） -->
        <view class="status-card">
          <image src="/static/icon/temp.png" class="status-icon" />
          <text class="status-value" :class="environment.tempStatus">{{ Math.round(environment.temp) }}℃</text>
          <text class="status-tip">{{ getTempTip(environment.tempStatus) }}</text>
        </view>
        
        <!-- 湿度卡片（显示整数） -->
        <view class="status-card">
          <image src="/static/icon/humidity.png" class="status-icon" />
          <text class="status-value" :class="environment.humidityStatus">{{ Math.round(environment.humidity) }}%</text>
          <text class="status-tip">{{ getHumidityTip(environment.humidityStatus) }}</text>
        </view>
        
        <!-- 更多按钮卡片 -->
        <view class="status-card more-card" @click="goToEnvMonitor">
          <image src="/static/icon/more.png" class="status-icon" />
          <text class="status-value">更多</text>
        </view>
      </view>

      <!-- 设备统计卡片 -->
      <view class="device-stat-card" @click="goToDeviceManage">
        <view class="stat-item">
          <text class="stat-label">设备数</text>
          <text class="stat-value">{{ currentSceneDeviceCount }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-label">在线</text>
          <text class="stat-value online">{{ currentSceneOnlineCount }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-label">已开启</text>
          <text class="stat-value active">{{ currentSceneActiveCount }}</text>
        </view>
        <image src="/static/icon/arrow-right.png" class="stat-arrow" />
      </view>

      <!-- 模式模块 -->
      <view class="modes">
        <view 
          v-for="(item, index) in modes" 
          :key="index" 
          :class="['mode-item', currentMode === item ? 'active' : '']"
          @click="activateMode(item)"
        >
          {{ item }}
          <view v-if="currentMode === item" class="active-indicator"></view>
        </view>
      </view>

      <!-- 设备卡片列表 -->
      <scroll-view class="devices-scroll" scroll-y>
        <view class="devices">
          <view 
            v-for="device in filteredDevices" 
            :key="device.id" 
            class="device-card"
          >
            <!-- 左侧信息区域 -->
            <view class="device-left">
              <image :src="device.on ? device.iconOn : device.iconOff" class="device-icon"/>
              <view class="info" @click="goToDevice(device)">
                <text class="device-name">{{ device.name }}</text>
                <text class="device-location">{{ device.location }}</text>
                <text class="device-desc">{{ device.online ? device.desc : '设备离线' }}</text>
                
                <!-- 空调温度调节控件 -->
                <view v-if="device.id === 'air' && device.on && device.online" class="temp-controls">
                  <button class="temp-btn minus" @click.stop="adjustTemperature(-1, device)">-</button>
                  <text class="current-temp">{{ device.temp }}℃</text>
                  <button class="temp-btn plus" @click.stop="adjustTemperature(1, device)">+</button>
                </view>
              </view>
            </view>
            
            <!-- 右侧开关 -->
            <switch 
              class="device-switch" 
              :checked="device.on" 
              @change="toggleDevice(device)"
              :disabled="!device.online"
            ></switch>
          </view>
          
          <!-- 底部留白 -->
          <view class="bottom-space"></view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentScene: "全屋",
      scenes: ["全屋", "客厅", "卧室", "卫生间"],
      modes: ["夜晚", "离家", "回家", "起床"],
      timer: null,
      timeUpdateTimer: null,
      currentTime: ""
    };
  },
  computed: {
    // 从Store获取环境数据
    environment() {
      return this.$store.getters.getEnvironment;
    },
    // 当前激活模式
    currentMode() {
      return this.$store.getters.getCurrentMode;
    },
    // 当前场景设备列表
    filteredDevices() {
      return this.$store.getters.getDevicesByScene(this.currentScene);
    },
    // 当前场景设备统计
    currentSceneDeviceCount() {
      return this.filteredDevices.length;
    },
    currentSceneOnlineCount() {
      return this.filteredDevices.filter(device => device.online).length;
    },
    currentSceneActiveCount() {
      return this.filteredDevices.filter(device => device.on && device.online).length;
    }
  },
  onLoad() {
    // 初始化时间
    this.updateTime();
    this.timeUpdateTimer = setInterval(() => this.updateTime(), 60000);
    
    // 环境数据更新
    this.timer = setInterval(() => {
      const currentEnv = this.$store.getters.getFullEnvironment;
      const newEnv = {
        temp: Math.max(20, Math.min(40, currentEnv.temp + (Math.random() - 0.5) * 2)),
        humidity: Math.max(10, Math.min(90, currentEnv.humidity + (Math.random() - 0.5) * 5)),
        gasConcentration: Math.max(0, Math.min(10, currentEnv.gasConcentration + (Math.random() - 0.5) * 1)),
        flameLevel: Math.round(Math.random()),
        smokeLevel: Math.round(Math.random())
      };
      this.$store.commit("UPDATE_FULL_ENVIRONMENT", newEnv);
    }, 5000);
  },
  onUnload() {
    clearInterval(this.timer);
    clearInterval(this.timeUpdateTimer);
  },
  methods: {
    // 更新时间显示
    updateTime() {
      const now = new Date();
      const hours = this.padZero(now.getHours());
      const minutes = this.padZero(now.getMinutes());
      this.currentTime = `${hours}:${minutes}`;
    },
    padZero(num) {
      return num < 10 ? `0${num}` : num;
    },
    // 空调温度调节
    adjustTemperature(change, device) {
      if (!device.online) return;
      const newTemp = Math.min(Math.max(device.temp + change, 16), 30);
      this.$store.commit("SET_AIR_TEMP", {
        deviceId: device.id,
        temp: newTemp
      });
    },
    // 切换场景
    changeScene(scene) {
      this.currentScene = scene;
    },
    // 切换设备开关
    toggleDevice(device) {
      this.$store.commit("TOGGLE_DEVICE_ON", device.id);
    },
    // 跳转到设备详情页
    goToDevice(device) {
      let page = '';
      if (device.id.includes('light')) {
        page = 'light';
      } else if (device.id === 'air') {
        page = 'air';
      } else if (device.id === 'shower') {
        page = 'shower';
      }
      uni.navigateTo({
        url: `/pages/device/${page}?deviceId=${device.id}`
      });
    },
    // 激活模式
    activateMode(modeName) {
      if (this.currentMode === modeName) {
        this.$store.commit("DEACTIVATE_MODE");
      } else {
        this.$store.commit("ACTIVATE_MODE", modeName);
      }
    },
    // 温度提示文本
    getTempTip(status) {
      const tipMap = { low: "偏低", normal: "", high: "偏高" };
      return tipMap[status];
    },
    // 湿度提示文本
    getHumidityTip(status) {
      const tipMap = { dry: "偏干", normal: "", wet: "偏湿" };
      return tipMap[status];
    },
    // 跳转到设备管理页
    goToDeviceManage() {
      uni.navigateTo({ url: "/pages/device/manage" });
    },
    // 跳转到环境监测详情页
    goToEnvMonitor() {
      uni.navigateTo({ url: "/pages/environment/monitor" });
    }
  }
};
</script>

<style scoped>
/* 基础容器样式 */
.page-container {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* 修复背景显示问题 */
.page {
  padding: 20rpx;
  font-family: "Arial", "PingFang SC", sans-serif;
  min-height: 100vh;
  background-repeat: no-repeat;
  box-sizing: border-box;
  /* 确保背景图覆盖整个页面且不重复 */
  background-attachment: fixed;
  background-position: center;
  background-size: cover;
}

/* 头部样式 */
.header {
  margin: 15rpx 0 20rpx;
}
.title {
  font-size: 32rpx;
  font-weight: bold;
  color: #007AFF;
  letter-spacing: 2rpx;
}

/* 场景导航 */
.scene-nav {
  display: flex;
  flex-direction: row;
  padding: 8rpx 0;
  white-space: nowrap;
  margin-bottom: 8rpx;
}
.scene-item {
  display: inline-block;
  padding: 12rpx 25rpx;
  margin-right: 15rpx;
  border-radius: 30rpx;
  background: rgba(255,255,255,0.7);
  font-size: 24rpx;
  color: #666;
  box-shadow: 0 2rpx 5rpx rgba(0,0,0,0.05);
}
.scene-item.active {
  background: #007AFF;
  color: #fff;
}

/* 状态显示区：紧凑布局，向左靠拢 */
.status-container {
  display: flex;
  align-items: center;
  gap: 8rpx; /* 缩小卡片间距 */
  margin: 10rpx 0;
  padding: 5rpx 0;
  overflow-x: auto;
  /* 去掉右侧滚动留白 */
  padding-left: 2rpx;
  padding-right: 2rpx;
}

/* 缩小状态卡片尺寸 */
.status-card {
  background: rgba(255, 255, 255, 0.85);
  border-radius: 15rpx;
  padding: 10rpx 15rpx; /* 减小内边距 */
  display: flex;
  align-items: center;
  min-width: 130rpx; /* 缩小卡片宽度 */
  box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.05);
}

.more-card {
  cursor: pointer;
}
.more-card:active {
  background: rgba(255,255,255,0.95);
}

.status-icon {
  width: 28rpx; /* 缩小图标 */
  height: 28rpx;
  margin-right: 8rpx;
  flex-shrink: 0;
}

.status-value {
  font-size: 22rpx; /* 缩小文字 */
  font-weight: 500;
  flex-shrink: 0;
}

.status-value.low, .status-value.dry { color: #007AFF; }
.status-value.normal { color: #333; }
.status-value.high, .status-value.wet { color: #FF3B30; }

.status-tip {
  font-size: 14rpx; /* 缩小提示文字 */
  color: inherit;
  margin-left: 4rpx;
  opacity: 0.8;
}

/* 设备统计卡片 */
.device-stat-card {
  background: rgba(255,255,255,0.9);
  border-radius: 20rpx;
  padding: 18rpx 25rpx;
  margin-bottom: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}
.stat-item {
  flex: 1;
  text-align: center;
}
.stat-label {
  font-size: 20rpx;
  color: #999;
  display: block;
}
.stat-value {
  font-size: 26rpx;
  font-weight: bold;
  color: #333;
  margin-top: 3rpx;
}
.stat-value.online { color: #00B42A; }
.stat-value.active { color: #FF7D00; }
.stat-arrow {
  width: 28rpx;
  height: 28rpx;
  margin-left: 8rpx;
}

/* 模式选择 */
.modes {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20rpx;
  padding: 0 8rpx;
}
.mode-item {
  width: 130rpx;
  height: 70rpx;
  background: rgba(255,255,255,0.7);
  border-radius: 20rpx;
  text-align: center;
  line-height: 70rpx;
  font-size: 24rpx;
  color: #333;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
  position: relative;
}
.mode-item.active {
  background: #007AFF;
  color: #fff;
}
.active-indicator {
  position: absolute;
  bottom: 4rpx;
  right: 4rpx;
  width: 14rpx;
  height: 14rpx;
  background-color: #fff;
  border-radius: 50%;
}

/* 设备列表滚动容器 */
.devices-scroll {
  flex: 1;
  height: calc(100vh - 420rpx);
  scrollbar-width: thin;
}
.devices-scroll::-webkit-scrollbar {
  width: 6rpx;
}
.devices-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(0,0,0,0.1);
  border-radius: 3rpx;
}

/* 设备卡片容器 */
.devices {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

/* 设备卡片样式 */
.device-card {
  background: rgba(255,255,255,0.9);
  border-radius: 18rpx;
  padding: 15rpx 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.05);
  min-height: 100rpx;
}
.device-card:hover {
  transform: translateY(-2rpx);
  box-shadow: 0 4rpx 10rpx rgba(0,0,0,0.08);
  transition: all 0.2s ease;
}
.device-left {
  display: flex;
  align-items: center;
  width: 82%;
}
.device-icon {
  width: 50rpx;
  height: 50rpx;
  margin-right: 18rpx;
}
.info {
  flex: 1;
  overflow: hidden;
  padding: 5rpx 0;
}
.info:active {
  background-color: rgba(0, 122, 255, 0.05);
  border-radius: 5rpx;
}
.device-name {
  font-size: 26rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 3rpx;
}
.device-location {
  font-size: 20rpx;
  color: #666;
  display: block;
  margin-bottom: 2rpx;
  opacity: 0.9;
}
.device-desc {
  font-size: 20rpx;
  color: #999;
}
.device-switch {
  transform: scale(0.85);
  z-index: 10;
}

/* 空调温度控制 */
.temp-controls {
  display: flex;
  align-items: center;
  margin-top: 5rpx;
  height: 36rpx;
}
.temp-btn {
  width: 36rpx;
  height: 36rpx;
  line-height: 36rpx;
  padding: 0;
  margin: 0 6rpx;
  border-radius: 50%;
  font-size: 24rpx;
  font-weight: bold;
  border: none;
  display: flex;
  justify-content: center;
  align-items: center;
}
.temp-btn.plus {
  background-color: #e6f7ff;
  color: #1890ff;
}
.temp-btn.minus {
  background-color: #fff1f0;
  color: #ff4d4f;
}
.current-temp {
  font-size: 22rpx;
  color: #007AFF;
  font-weight: 500;
}

/* 底部留白 */
.bottom-space {
  height: 30rpx;
}
</style>
    