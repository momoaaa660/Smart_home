import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    // 设备状态：包含原有设备+新增卧室灯光
    devices: {
      // 原有灯光设备
      light_living: {
        id: 'light_living',
        name: '主灯',
        location: '客厅',
        on: false,
        iconOn: '/static/icon/light_on.png',
        iconOff: '/static/icon/light_off.png',
        scene: '客厅',
        online: true,
        desc: '已关闭'
      },
      light_bedroom: {
        id: 'light_bedroom',
        name: '卧室主灯',
        location: '卧室',
        on: false,
        iconOn: '/static/icon/light_on.png',
        iconOff: '/static/icon/light_off.png',
        scene: '卧室',
        online: true,
        desc: '已关闭'
      },
      light_bathroom: {
        id: 'light_bathroom',
        name: '镜前灯',
        location: '卫生间',
        on: false,
        iconOn: '/static/icon/light_on.png',
        iconOff: '/static/icon/light_off.png',
        scene: '卫生间',
        online: true,
        desc: '已关闭'
      },
      // 新增卧室灯光
      light_bedside: {
        id: 'light_bedside',
        name: '床头灯',
        location: '卧室',
        on: false,
        iconOn: '/static/icon/light_on.png',
        iconOff: '/static/icon/light_off.png',
        scene: '卧室',
        online: true,
        desc: '已关闭'
      },
      light_desk: {
        id: 'light_desk',
        name: '书桌台灯',
        location: '卧室',
        on: false,
        iconOn: '/static/icon/light_on.png',
        iconOff: '/static/icon/light_off.png',
        scene: '卧室',
        online: true,
        desc: '已关闭'
      },
      // 空调设备
      air: {
        id: 'air',
        name: '空调',
        location: '卧室',
        on: false,
        temp: 26,
        mode: 'cool', // cool, heat, auto
        iconOn: '/static/icon/air_on.png',
        iconOff: '/static/icon/air_off.png',
        scene: '卧室',
        online: true,
        desc: '制冷 26℃'
      },
      // 淋浴设备
      shower: {
        id: 'shower',
        name: '热水器',
        location: '卫生间',
        on: false,
        temp: 45,
        iconOn: '/static/icon/shower_on.png',
        iconOff: '/static/icon/shower_off.png',
        scene: '卫生间',
        online: true,
        desc: '水温 45℃'
      }
    },
    // 当前激活的模式
    currentMode: null,
    // 完整环境数据（支持温湿度、可燃气体、火焰、烟雾）
    environment: {
      temp: 25,          // 温度(℃)
      humidity: 50,      // 湿度(%)
      gasConcentration: 3, // 可燃气体浓度(ppm)
      flameLevel: 0,     // 火焰等级(0-5)
      smokeLevel: 0,     // 烟雾等级(0-5)
      // 主页用温湿度状态标识
      tempStatus: 'normal',  // low, normal, high
      humidityStatus: 'normal' // dry, normal, wet
    }
  },
  mutations: {
    // 1. 切换设备开关状态（原有逻辑不变）
    TOGGLE_DEVICE_ON(state, deviceId) {
      const device = state.devices[deviceId]
      if (device) {
        device.on = !device.on
        if (deviceId.includes('light_')) {
          device.desc = device.on ? '已开启' : '已关闭'
        }
      }
    },
    // 2. 空调温度更新（原有逻辑不变）
    SET_AIR_TEMP(state, { deviceId, temp }) {
      if (deviceId === 'air' && state.devices.air) {
        state.devices.air.temp = temp
        const modeText = { cool: '制冷', heat: '制热', auto: '自动' }
        state.devices.air.desc = `${modeText[state.devices.air.mode]} ${temp}℃`
      }
    },
    // 3. 空调模式更新（原有逻辑不变）
    SET_AIR_MODE(state, { deviceId, mode }) {
      if (deviceId === 'air' && state.devices.air) {
        state.devices.air.mode = mode
        const modeText = { cool: '制冷', heat: '制热', auto: '自动' }
        state.devices.air.desc = `${modeText[mode]} ${state.devices.air.temp}℃`
      }
    },
    // 4. 淋浴设备温度更新（原有逻辑不变）
    SET_SHOWER_TEMP(state, { deviceId, temp }) {
      if (deviceId === 'shower' && state.devices.shower) {
        state.devices.shower.temp = temp
        state.devices.shower.desc = `水温 ${temp}℃`
      }
    },
    // 5. 更新完整环境数据（新增：支持所有监测项）
    UPDATE_FULL_ENVIRONMENT(state, newEnvData) {
      // 合并新数据到原有环境状态
      state.environment = { ...state.environment, ...newEnvData }
      
      // 同步更新温湿度状态标识（供主页使用）
      // 温度状态：<20低，20-26正常，>26高
      if (state.environment.temp < 20) {
        state.environment.tempStatus = 'low'
      } else if (state.environment.temp > 26) {
        state.environment.tempStatus = 'high'
      } else {
        state.environment.tempStatus = 'normal'
      }
      
      // 湿度状态：<30干，30-60正常，>60湿
      if (state.environment.humidity < 30) {
        state.environment.humidityStatus = 'dry'
      } else if (state.environment.humidity > 60) {
        state.environment.humidityStatus = 'wet'
      } else {
        state.environment.humidityStatus = 'normal'
      }
    },
    // 6. 激活模式（原有逻辑不变，已适配新增灯光）
    ACTIVATE_MODE(state, modeName) {
      state.currentMode = modeName
      const modeConfig = {
        '夜晚': {
          light_living: { on: false },
          light_bedroom: { on: false },
          light_bedside: { on: true },
          light_desk: { on: false },
          light_bathroom: { on: false },
          air: { on: true, temp: 26, mode: 'auto' },
          shower: { on: false }
        },
        '离家': {
          light_living: { on: false },
          light_bedroom: { on: false },
          light_bedside: { on: false },
          light_desk: { on: false },
          light_bathroom: { on: false },
          air: { on: false },
          shower: { on: false }
        },
        '回家': {
          light_living: { on: true },
          light_bedroom: { on: false },
          light_bedside: { on: false },
          light_desk: { on: false },
          light_bathroom: { on: false },
          air: { on: true, temp: 26, mode: 'cool' },
          shower: { on: false }
        },
        '起床': {
          light_living: { on: false },
          light_bedroom: { on: true },
          light_bedside: { on: true },
          light_desk: { on: true },
          light_bathroom: { on: true },
          air: { on: true, temp: 26, mode: 'cool' },
          shower: { on: false }
        }
      }
      
      if (modeConfig[modeName]) {
        Object.keys(modeConfig[modeName]).forEach(deviceId => {
          const config = modeConfig[modeName][deviceId]
          const device = state.devices[deviceId]
          if (device) {
            Object.assign(device, config)
            if (deviceId.includes('light_')) {
              device.desc = device.on ? '已开启' : '已关闭'
            } else if (deviceId === 'air') {
              const modeText = { cool: '制冷', heat: '制热', auto: '自动' }
              device.desc = `${modeText[device.mode]} ${device.temp}℃`
            } else if (deviceId === 'shower') {
              device.desc = `水温 ${device.temp}℃`
            }
          }
        })
      }
    },
    // 7. 取消激活模式（原有逻辑不变）
    DEACTIVATE_MODE(state) {
      state.currentMode = null
    },
    // 8. 重命名设备（原有逻辑不变）
    RENAME_DEVICE(state, { id, name }) {
      if (state.devices[id]) {
        state.devices[id].name = name
      }
    },
    // 9. 删除设备（原有逻辑不变，保护默认设备）
    DELETE_DEVICE(state, deviceId) {
      const defaultDevices = ['light_living', 'light_bedroom', 'light_bathroom', 'light_bedside', 'light_desk', 'air', 'shower']
      if (state.devices[deviceId] && !defaultDevices.includes(deviceId)) {
        delete state.devices[deviceId]
      }
    }
  },
  getters: {
    // 主页用环境数据（仅返回温湿度+状态）
    getEnvironment: (state) => ({
      temp: state.environment.temp,
      humidity: state.environment.humidity,
      tempStatus: state.environment.tempStatus,
      humidityStatus: state.environment.humidityStatus
    }),
    // 环境监测页用完整环境数据（所有监测项）
    getFullEnvironment: (state) => state.environment,
    // 当前激活模式（原有逻辑不变）
    getCurrentMode: (state) => state.currentMode,
    // 按ID获取设备（原有逻辑不变）
    getDeviceById: (state) => (id) => state.devices[id] || null,
    // 按场景获取设备（原有逻辑不变）
    getDevicesByScene: (state) => (scene) => {
      return Object.values(state.devices).filter(device => 
        scene === '全屋' || device.scene === scene
      )
    },
    // 设备统计（原有逻辑不变）
    getTotalDeviceCount: (state) => Object.keys(state.devices).length,
    getOnlineDeviceCount: (state) => Object.values(state.devices).filter(d => d.online).length,
    getActiveDeviceCount: (state) => Object.values(state.devices).filter(d => d.on && d.online).length,
    // 获取所有灯光设备（原有逻辑不变）
    getAllLights: (state) => {
      return Object.values(state.devices).filter(device => device.id.includes('light_'))
    }
  }
})