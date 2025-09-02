<template>
  <view class="page-container">
    <!-- 带背景的页面，与主页风格统一 -->
    <view class="page" :style="{ backgroundImage: 'url(/static/img/home_bg.png)', backgroundSize: 'cover' }">
      <!-- 时间范围选择 -->
      <view class="time-range">
        <view class="time-item" 
          v-for="item in timeRanges" 
          :key="item.value"
          :class="{ 'active': selectedTimeRange === item.value }"
          @click="selectTimeRange(item.value)">
          {{ item.label }}
        </view>
      </view>
      
      <!-- 图表容器 -->
      <view class="chart-container">
        <view class="chart-wrapper">
          <canvas canvas-id="lineCanvas" class="line-chart"></canvas>
        </view>
        
        <!-- 数据统计摘要 -->
        <view class="stats-summary">
          <view class="stat-item">
            <text class="stat-label">平均值</text>
            <text class="stat-value">{{ stats.average.toFixed(1) }}{{ unit }}</text>
          </view>
          <view class="stat-item">
            <text class="stat-label">最大值</text>
            <text class="stat-value">{{ stats.max.toFixed(1) }}{{ unit }}</text>
          </view>
          <view class="stat-item">
            <text class="stat-label">最小值</text>
            <text class="stat-value">{{ stats.min.toFixed(1) }}{{ unit }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      chartType: 'temperature', // 默认显示温度统计
      selectedTimeRange: 'day', // 默认显示24小时数据
      timeRanges: [
        { label: '3小时', value: '3hours' },
        { label: '24小时', value: 'day' },
        { label: '15天', value: '15days' }
      ],
      chartData: [],
      stats: {
        average: 0,
        max: 0,
        min: 0
      },
      chart: null,
      // 提供初始的模拟数据，确保页面初次加载时有内容显示
      initialMockData: {
        temperature: [],
        humidity: []
      }
    };
  },
  
  computed: {
    // 图表标题
    chartTitle() {
      return this.chartType === 'temperature' ? '温度' : '湿度';
    },
    
    // 数据单位
    unit() {
      return this.chartType === 'temperature' ? '°C' : '%';
    },
    
    // 从Vuex获取当前环境数据
    currentEnvData() {
      return this.$store.getters.getFullEnvironment;
    }
  },
  
  onLoad(options) {
    // 接收从monitor页面传递的参数
    if (options && options.type) {
      this.chartType = options.type;
    }
    
    // 初始化模拟历史数据
    this.generateInitialMockData();
    
    // 初始化图表数据
    this.generateChartData();
  },
  
  onShow() {
    // 每次页面显示时，重新生成数据，确保与index页面数据保持同步
    this.generateChartData();
    this.drawChart();
  },
  
  onReady() {
    // 页面渲染完成后绘制图表
    this.drawChart();
  },
  
  watch: {
    // 监听环境数据变化，实时更新图表
    currentEnvData: {
      handler() {
        this.generateChartData();
        this.drawChart();
      },
      deep: true // 深度监听对象内部变化
    },
    
    // 监听图表类型变化
    chartType() {
      this.generateChartData();
      this.drawChart();
    }
  },
  
  methods: {
    // 返回上一页
    navigateBack() {
      uni.navigateBack();
    },
    
    // 生成初始的模拟历史数据
    generateInitialMockData() {
      // 从store初始化环境历史数据
      this.$store.dispatch('initializeApp');
    },
    
    // 选择时间范围
    selectTimeRange(range) {
      this.selectedTimeRange = range;
      this.generateChartData();
      this.drawChart();
    },
    
    // 生成图表数据
    generateChartData() {
      // 时间范围映射
      const rangeMapping = {
        '3hours': '10min',
        'day': 'hourly',
        '15days': 'daily'
      };
      
      // 获取映射后的粒度
      const granularity = rangeMapping[this.selectedTimeRange] || 'hourly';
      const type = this.chartType === 'temperature' ? 'temperature' : 'humidity';
      
      // 获取真实的历史环境数据（修正参数顺序）
      const historyData = this.$store.getters.getEnvironmentHistory(granularity, type);
      
      const data = [];
      let timeFormat = 'HH:mm'; // 默认时间格式
      
      // 根据不同的时间范围设置不同的时间格式
      if (this.selectedTimeRange === '3hours') {
        timeFormat = 'HH:mm';
      } else if (this.selectedTimeRange === 'day') {
        timeFormat = 'HH:mm';
      } else if (this.selectedTimeRange === '15days') {
        timeFormat = 'MM-DD';
      } else {
        timeFormat = 'HH:mm';
      }
      
      // 处理历史数据，格式化为图表需要的格式
      if (historyData && historyData.length > 0) {
        historyData.forEach(item => {
          const date = new Date(item.time);
          
          data.push({
            time: this.formatTime(date, timeFormat),
            value: item.value
          });
        });
      } else {
        // 如果没有历史数据，使用当前环境数据生成一些默认数据点
        const now = new Date();
        const currentValue = this.chartType === 'temperature' ? this.currentEnvData.temp : this.currentEnvData.humidity;
        let dataPoints = 24;
        
        if (this.selectedTimeRange === '3hours') {
          dataPoints = 18; // 3小时，每10分钟一个点，共18个点
        } else if (this.selectedTimeRange === '15days') {
          dataPoints = 15;
        }
        
        for (let i = dataPoints - 1; i >= 0; i--) {
          const time = new Date(now);
          
          if (this.selectedTimeRange === '3hours') {
            time.setMinutes(now.getMinutes() - i * 10); // 每10分钟一个点
          } else if (this.selectedTimeRange === 'day') {
            time.setHours(now.getHours() - i);
          } else if (this.selectedTimeRange === '15days') {
            time.setDate(now.getDate() - i);
            time.setHours(12, 0, 0, 0);
          }
          
          const variation = this.chartType === 'temperature' ? (Math.random() - 0.5) * 4 : (Math.random() - 0.5) * 15;
          const newValue = Math.max(0, Math.min(
            this.chartType === 'temperature' ? 40 : 100,
            currentValue + variation
          ));
          
          data.push({
            time: this.formatTime(time, timeFormat),
            value: Number(newValue.toFixed(1))
          });
        }
      }
      
      this.chartData = data;
      this.calculateStats();
    },
    
    // 格式化时间
    formatTime(date, format) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      
      if (format === 'HH:mm') {
        return `${hours}:${minutes}`;
      } else if (format === 'MM-DD') {
        return `${month}-${day}`;
      }
      
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    },
    
    // 计算统计数据
    calculateStats() {
      if (this.chartData.length === 0) {
        this.stats = { average: 0, max: 0, min: 0 };
        return;
      }
      
      const values = this.chartData.map(item => item.value);
      const sum = values.reduce((acc, val) => acc + val, 0);
      
      this.stats = {
        average: sum / values.length,
        max: Math.max(...values),
        min: Math.min(...values)
      };
    },
    
    // 绘制折线图
    drawChart() {
      try {
        // 使用uni.createCanvasContext代替wx.createCanvasContext，确保更好的跨平台兼容性
        const ctx = uni.createCanvasContext('lineCanvas');
        const chartWidth = wx.getSystemInfoSync().windowWidth - 60;
        const chartHeight = 300;
        
        // 清空画布
        ctx.clearRect(0, 0, chartWidth, chartHeight);
      
      if (this.chartData.length === 0) {
          // 确保即使没有数据也执行draw()
          ctx.draw();
          return;
        }
      
      // 15日数据需要按照时间从旧到新排列
      let displayData = this.chartData;
      if (this.selectedTimeRange === '15days') {
        // 复制原始数据并按时间排序
        displayData = [...this.chartData].sort((a, b) => {
          // 解析日期字符串并比较
          const dateA = new Date(a.time);
          const dateB = new Date(b.time);
          return dateA - dateB;
        });
      }
      
      // 计算数据范围
      const values = displayData.map(item => item.value);
      const minValue = Math.min(...values);
      const maxValue = Math.max(...values);
      const valueRange = maxValue - minValue || 1; // 防止除以0
      
      // 图表边距
      const padding = 40;
      const plotWidth = chartWidth - 2 * padding;
      const plotHeight = chartHeight - 2 * padding;
      
      // 绘制坐标轴
      ctx.setStrokeStyle('#e0e0e0');
      ctx.setLineWidth(1);
      
      // X轴
      ctx.beginPath();
      ctx.moveTo(padding, chartHeight - padding);
      ctx.lineTo(chartWidth - padding, chartHeight - padding);
      ctx.stroke();
      
      // Y轴
      ctx.beginPath();
      ctx.moveTo(padding, padding);
      ctx.lineTo(padding, chartHeight - padding);
      ctx.stroke();
      
      // 绘制网格线
      ctx.setStrokeStyle('#f0f0f0');
      ctx.setLineWidth(1);
      
      // 水平网格线
      for (let i = 0; i <= 4; i++) {
        const y = padding + (plotHeight / 4) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(chartWidth - padding, y);
        ctx.stroke();
        
        // Y轴刻度标签
        const value = maxValue - (valueRange / 4) * i;
        ctx.setFillStyle('#999');
        ctx.setFontSize(12);
        ctx.textAlign = 'right';
        ctx.fillText(value.toFixed(1), padding - 10, y + 5);
      }
      
      // X轴刻度标签
      const labelStep = Math.max(1, Math.floor(displayData.length / 6));
      ctx.setFillStyle('#999');
      ctx.setFontSize(12);
      ctx.textAlign = 'center';
      
      for (let i = 0; i < displayData.length; i += labelStep) {
        const x = padding + (plotWidth / (displayData.length - 1)) * i;
        const y = chartHeight - padding + 20;
        ctx.fillText(displayData[i].time, x, y);
      }
      
      // 绘制折线
      const lineColor = this.chartType === 'temperature' ? '#007AFF' : '#00B42A';
      ctx.setStrokeStyle(lineColor);
      ctx.setLineWidth(3);
      ctx.setLineCap('round');
      ctx.setLineJoin('round');
      
      ctx.beginPath();
      displayData.forEach((item, index) => {
        const x = padding + (plotWidth / (displayData.length - 1)) * index;
        const y = padding + plotHeight - ((item.value - minValue) / valueRange) * plotHeight;
        
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
      
      // 绘制数据点
      ctx.setFillStyle(lineColor);
      displayData.forEach((item, index) => {
        const x = padding + (plotWidth / (displayData.length - 1)) * index;
        const y = padding + plotHeight - ((item.value - minValue) / valueRange) * plotHeight;
        
        // 绘制外圈
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, 2 * Math.PI);
        ctx.setFillStyle('#fff');
        ctx.fill();
        ctx.setStrokeStyle(lineColor);
        ctx.setLineWidth(2);
        ctx.stroke();
      });
      
      // 绘制填充区域
      ctx.beginPath();
      ctx.moveTo(padding, chartHeight - padding);
      displayData.forEach((item, index) => {
        const x = padding + (plotWidth / (displayData.length - 1)) * index;
        const y = padding + plotHeight - ((item.value - minValue) / valueRange) * plotHeight;
        
        if (index === 0) {
          ctx.lineTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.lineTo(chartWidth - padding, chartHeight - padding);
      ctx.closePath();
      
      // 创建渐变填充
      const gradient = ctx.createLinearGradient(padding, padding, padding, chartHeight - padding);
      const gradientStartColor = this.chartType === 'temperature' ? 'rgba(0, 122, 255, 0.2)' : 'rgba(0, 180, 42, 0.2)';
      const gradientEndColor = this.chartType === 'temperature' ? 'rgba(0, 122, 255, 0.05)' : 'rgba(0, 180, 42, 0.05)';
      gradient.addColorStop(0, gradientStartColor);
      gradient.addColorStop(1, gradientEndColor);
      
      ctx.setFillStyle(gradient);
      ctx.fill();
      
      // 绘制图表
        ctx.draw();
      } catch (error) {
        console.error('绘制图表出错:', error);
      }
    }
  }
};
</script>

<style scoped>
/* 基础容器样式，与主页保持一致 */
.page-container {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.page {
  padding: 20rpx;
  font-family: "Arial", "PingFang SC", sans-serif;
  min-height: 100vh;
  background-repeat: no-repeat;
  box-sizing: border-box;
}

/* 头部样式，与主页风格统一 */
.header {
  display: flex;
  align-items: center;
  margin: 30rpx 0;
}

.back {
  font-size: 36rpx;
  color: #333;
  margin-right: 20rpx;
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back:active {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 50%;
}

.title {
  font-size: 32rpx;
  font-weight: 500;
  color: #333;
  flex: 1;
  text-align: center;
}

/* 时间范围选择器 */
.time-range {
  display: flex;
  justify-content: center;
  margin: 20rpx 0;
  padding: 0 20rpx;
}

.time-item {
  padding: 10rpx 30rpx;
  margin: 0 10rpx;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #666;
  box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.05);
}

.time-item.active {
  background: #007AFF;
  color: #fff;
}

/* 图表容器 */
.chart-container {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20rpx;
  padding: 30rpx 20rpx;
  margin: 20rpx 0;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

/* 图表包装器 */
.chart-wrapper {
  width: 100%;
  height: 300px;
  margin-bottom: 30rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 折线图 */
.line-chart {
  width: 100%;
  height: 100%;
}

/* 统计摘要 */
.stats-summary {
  display: flex;
  justify-content: space-around;
  padding: 10rpx 0;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-label {
  font-size: 20rpx;
  color: #999;
  display: block;
  margin-bottom: 8rpx;
}

.stat-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}
</style>