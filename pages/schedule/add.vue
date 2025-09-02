<template>
  <view class="page">
    <!-- 自定义导航栏 -->
    <view class="nav-bar">
      <view class="nav-left" @click="goBack">
        <text class="nav-back">←</text>
      </view>
      <view class="nav-center">
        <text class="nav-title">{{ isEdit ? '编辑日程' : '添加日程' }}</text>
      </view>
      <view class="nav-right" @click="saveSchedule">
        <text class="nav-save" :class="{ disabled: !canSave }">保存</text>
      </view>
    </view>

    <!-- 表单内容 -->
    <scroll-view class="content" scroll-y>
      <!-- 日程标题 -->
      <view class="form-section">
        <view class="form-item">
          <text class="form-label">标题</text>
          <input 
            class="form-input" 
            v-model="formData.title" 
            placeholder="请输入日程标题"
            maxlength="30"
          />
        </view>
      </view>

      <!-- 日期时间 -->
      <view class="form-section">
        <view class="form-item">
          <text class="form-label">日期</text>
          <picker mode="date" :value="formData.date" @change="onDateChange">
            <view class="form-picker">
              <text class="picker-text">{{ formData.date || '请选择日期' }}</text>
              <text class="picker-arrow">></text>
            </view>
          </picker>
        </view>

        <view class="form-item">
          <text class="form-label">时间</text>
          <picker mode="time" :value="formData.time" @change="onTimeChange">
            <view class="form-picker">
              <text class="picker-text">{{ formData.time || '请选择时间' }}</text>
              <text class="picker-arrow">></text>
            </view>
          </picker>
        </view>
      </view>

      <!-- 优先级 -->
      <view class="form-section">
        <view class="section-title">
          <text class="form-label">优先级</text>
        </view>
        <view class="priority-grid">
          <view 
            v-for="priority in priorityOptions" 
            :key="priority.value"
            :class="['priority-card', priority.value, formData.priority === priority.value ? 'active' : '']"
            @click="selectPriority(priority.value)"
          >
            <text class="priority-text">{{ priority.label }}</text>
          </view>
        </view>
      </view>

      <!-- 地点 -->
      <view class="form-section">
        <view class="form-item">
          <text class="form-label">地点</text>
          <input 
            class="form-input" 
            v-model="formData.location" 
            placeholder="请输入地点"
            maxlength="50"
          />
        </view>
      </view>

      <!-- 描述 -->
      <view class="form-section">
        <view class="form-item">
          <text class="form-label">描述</text>
          <textarea 
            class="form-textarea" 
            v-model="formData.description" 
            placeholder="请输入日程描述"
            maxlength="200"
            auto-height
          ></textarea>
        </view>
      </view>

      <!-- 底部间距 -->
      <view class="bottom-space"></view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      isEdit: false,
      editId: null,
      formData: {
        title: '',
        date: '',
        time: '',
        location: '',
        description: '',
        priority: 'medium',
        completed: false
      },
      priorityOptions: [
        { label: '低', value: 'low' },
        { label: '中', value: 'medium' },
        { label: '高', value: 'high' }
      ]
    };
  },
  computed: {
    canSave() {
      return this.formData.title.trim() && this.formData.date && this.formData.time;
    }
  },
  onLoad(options) {
    // 获取传递的参数
    if (options.date) {
      this.formData.date = options.date;
    } else {
      this.formData.date = this.getTodayString();
    }
    
    if (options.time) {
      this.formData.time = options.time;
    } else {
      this.formData.time = this.getCurrentTime();
    }

    // 如果是编辑模式
    if (options.id) {
      this.isEdit = true;
      this.editId = parseInt(options.id);
      this.loadEditData();
    }
  },
  methods: {
    // 加载编辑数据
    loadEditData() {
      const schedules = this.$store.getters.getAllSchedules;
      const editSchedule = schedules.find(s => s.id == this.editId);
      if (editSchedule) {
        this.formData = { ...editSchedule };
      }
    },

    // 获取今天日期字符串
    getTodayString() {
      const today = new Date();
      const year = today.getFullYear();
      const month = today.getMonth() + 1;
      const day = today.getDate();
      return `${year}-${month < 10 ? '0' + month : month}-${day < 10 ? '0' + day : day}`;
    },

    // 获取当前时间
    getCurrentTime() {
      const now = new Date();
      let hours = now.getHours();
      let minutes = Math.ceil(now.getMinutes() / 15) * 15;
      
      if (minutes >= 60) {
        hours += 1;
        minutes = 0;
      }
      
      return `${hours < 10 ? '0' + hours : hours}:${minutes === 0 ? '00' : (minutes < 10 ? '0' + minutes : minutes)}`;
    },

    // 日期选择
    onDateChange(e) {
      this.formData.date = e.detail.value;
    },

    // 时间选择
    onTimeChange(e) {
      this.formData.time = e.detail.value;
    },

    // 选择优先级
    selectPriority(priority) {
      this.formData.priority = priority;
    },

    // 保存日程
    saveSchedule() {
      if (!this.canSave) {
        uni.showToast({
          title: '请填写必填项',
          icon: 'none'
        });
        return;
      }

      const scheduleData = {
        ...this.formData,
        title: this.formData.title.trim(),
        location: this.formData.location.trim(),
        description: this.formData.description.trim()
      };

      if (this.isEdit) {
        // 编辑模式
        this.$store.commit('UPDATE_SCHEDULE', {
          id: this.editId,
          updates: scheduleData
        });
        uni.showToast({
          title: '更新成功',
          icon: 'success'
        });
      } else {
        // 新增模式
        this.$store.commit('ADD_SCHEDULE', scheduleData);
        uni.showToast({
          title: '添加成功',
          icon: 'success'
        });
      }

      // 延迟返回，让用户看到成功提示
      setTimeout(() => {
        this.goBack();
      }, 1000);
    },

    // 返回
    goBack() {
      uni.navigateBack();
    }
  }
};
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f8f9fa;
}

.nav-bar {
  display: flex;
  align-items: center;
  height: 88rpx;
  padding: 0 32rpx;
  background: #fff;
  border-bottom: 1rpx solid #e6e6e6;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.nav-left {
  width: 120rpx;
}

.nav-back {
  font-size: 36rpx;
  color: #007AFF;
  font-weight: bold;
}

.nav-center {
  flex: 1;
  text-align: center;
}

.nav-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.nav-right {
  width: 120rpx;
  text-align: right;
}

.nav-save {
  font-size: 28rpx;
  color: #007AFF;
  font-weight: 500;
}

.nav-save.disabled {
  color: #ccc;
}

.content {
  padding-top: 88rpx;
  height: calc(100vh - 88rpx);
}

.form-section {
  background: #fff;
  margin-bottom: 20rpx;
  padding: 32rpx;
}

.form-item {
  display: flex;
  align-items: center;
  min-height: 88rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.form-item:last-child {
  border-bottom: none;
}

.form-label {
  width: 120rpx;
  font-size: 28rpx;
  color: #333;
  flex-shrink: 0;
}

.form-input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  padding: 20rpx 0;
}

.form-picker {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
}

.picker-text {
  font-size: 28rpx;
  color: #333;
}

.picker-arrow {
  font-size: 24rpx;
  color: #ccc;
}

.form-textarea {
  flex: 1;
  min-height: 200rpx;
  font-size: 28rpx;
  color: #333;
  padding: 20rpx 0;
  line-height: 1.5;
}

.section-title {
  margin-bottom: 24rpx;
}

.priority-grid {
  display: flex;
  gap: 24rpx;
}

.priority-card {
  flex: 1;
  padding: 24rpx 16rpx;
  text-align: center;
  background: #f8f9fa;
  border-radius: 12rpx;
  border: 2rpx solid transparent;
}

.priority-card:active {
  opacity: 0.7;
}

.priority-card.active {
  background: rgba(0, 122, 255, 0.1);
  border-color: #007AFF;
}

.priority-card.high.active {
  background: rgba(255, 71, 87, 0.1);
  border-color: #ff4757;
}

.priority-card.low.active {
  background: rgba(46, 213, 115, 0.1);
  border-color: #2ed573;
}

.priority-text {
  font-size: 26rpx;
  color: #666;
}

.priority-card.active .priority-text {
  color: #007AFF;
  font-weight: 500;
}

.priority-card.high.active .priority-text {
  color: #ff4757;
}

.priority-card.low.active .priority-text {
  color: #2ed573;
}

.bottom-space {
  height: 100rpx;
}
</style>