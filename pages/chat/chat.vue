<template>
	<!-- 页面根容器 -->
	<view class="container">
		<!-- 自定义声明组件，通过ref引用为"dialog" -->
		<statement ref="dialog"></statement>
		
		<!-- 聊天区域，id为"test"，通过ref引用为"chatbox" -->
		<view class="chat_area" id="test" ref="chatbox">
			<!-- 当前时间显示区域，仅当chatList有内容时显示 -->
			<view class="current_time" v-show="chatList.length>0">
				{{currentDate}}  <!-- 显示当前日期 -->
			</view>
			
			<!-- 左侧消息容器（机器人消息） -->
			<view class="left_box">
				<!-- 内容容器 -->
				<view class="content_box">
					<!-- 内容区域，使用post样式 -->
					<view class="content post">
						<!-- 欢迎消息 -->
						<view>我是您的智能家居助手，很高兴为您服务。</view>
						<view>您可以这样提出需求：</view>
						<!-- 示例问题区域 -->
						<view class="post_request">
							<!-- 遍历postRequest数组生成示例问题 -->
							<view v-for="(item,index) in postRequest" :key="index">
								<!-- 可点击的问题文本，点击触发tapQuestion方法 -->
								<text class="active" @click="tapQuestion(item)">
									{{item.id}}.{{item.text}}</text>
							</view>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 遍历chatList数组生成聊天记录 -->
			<view v-for="(item,i) in chatList" :key="i">
				<!-- 如果是助手(assistant)的消息，使用左侧布局 -->
				<view class="left_box" v-if="item.role == 'assistant'">
					<!-- 内容容器 -->
					<view class="content_box">
						<!-- 使用v-html渲染内容，通过htmlContent方法处理 -->
						<view class="content" v-html="htmlContent(item.content)">
						</view>
					</view>
				</view>

				<!-- 如果是用户(user)的消息，使用右侧布局 -->
				<view class="right_box" v-if="item.role == 'user'">
					<!-- 内容容器 -->
					<view class="content_box">
						<!-- 显示用户消息内容 -->
						<view class="content">
							{{item.content}}
						</view>
					</view>
				</view>
			</view>

			<!-- 加载指示器组件，根据showLoading状态显示/隐藏 -->
			<u-loading-icon text="响应中，请稍后..." textSize="16" :show="showLoading && !showTimeoutError && !showConnectionError"></u-loading-icon>
			
			<!-- 超时错误提示 -->
			<view v-if="showTimeoutError" class="error_message">
				<text>服务器繁忙，请稍后重试</text>
			</view>
			
			<!-- 连接错误提示 -->
			<view v-if="showConnectionError" class="error_message">
				<text>连接失败，请稍后再试</text>
			</view>
		</view>
		
		<!-- 底部输入区域 -->
		<view class="input_tab">
			<!-- 服务说明 -->
			<view class="statement">智能家居服务<text @tap="exemptStatement">使用说明</text></view>
			<!-- 输入组件区域 -->
			<view class="input_com">
				<!-- 左侧输入区域 -->
				<view class="left">
					<!-- 发送图标 -->
					<image src="../../static/icon/send.png"></image>
					<!-- 输入框，绑定userQuesion变量，设置占位符和光标间距 -->
					<input placeholder="请输入问题" v-model.trim="userQuesion" cursor-spacing="30rpx"></input>
				</view>
				<!-- 发送按钮，点击触发sendMsg方法，移除右边距使其紧贴输入框 -->
				<view class="send_btn" @tap="sendMsg">发送</view>
			</view>
		</view>
	</view>
</template>

<script>
	// 导入位于相对路径"../../components/statement.vue"的statement组件
	import statement from "../../components/statement.vue";
	// 从marked库中导入marked函数，用于将Markdown文本转换为HTML
	import { marked } from "marked";
	// 导出一个Vue组件对象
	export default {
		// 注册导入的statement组件，使其可在模板中使用
		components: {
			statement
		},
		// 定义组件的数据对象
		data() {
			// 开始返回数据对象
			return {
				// 用户头像图片URL，初始为空字符串
				userImg: '',
				// 默认用户头像图片路径
				nullImg: '../../static/icon/user.png',
				// 控制是否显示加载状态的标志位
				showLoading: false,
				// 预设的问题请求数组
				postRequest: [
					{ id: 1, text: '把空调温度调低一点' },
					{ id: 2, text: '打开卧室灯' },
					{ id: 3, text: '显示当前气温' }
				],
				// 存储聊天记录的数组
				chatList: [],
				// 存储用户输入的问题
				userQuesion: '',
				// 存储机器人的回答
				robotAnswer: '',
				// 存储当前时间
				currentDate: '',
				// 存储DOM元素的高度
				domHeight: 0,
				// 初始化与AI对话的消息数组，第一条为系统角色设定消息
				messages: [
					{
						role: "system",
						content: "你是一名专业的智能家居助手，专注于帮助用户控制家居设备（如灯光、空调、热水器）、查询设备状态和执行场景模式。当用户询问与智能家居无关的问题时，礼貌拒绝并引导至相关功能。"
					}
				],
				// 超时定时器ID
				timeoutTimer: null,
				// 响应超时时间（毫秒），默认30秒
				responseTimeout: 30000,
				// 是否显示超时错误信息
				showTimeoutError: false,
				// 是否显示连接错误信息
				showConnectionError: false,
				// WebSocket实例
				socketTask: null,
				// 连接状态
				connected: false,
				// 聊天历史记录
				history: []
			};
		},
		// 页面加载生命周期函数
		onLoad(option) {
			// 如果没有传入questionText参数则直接返回
			if (!option.questionText) return;
			this.userQuesion = option.questionText;
			// 将传入的参数questionText赋值给userQuesion
			this.sendMsg();
		},
		// 定义侦听器
		watch: {
			// 监听chatList数组长度的变化
			'chatList.length': {
				// 立即执行且深度监听
				immediate: true,
				deep: true,
				// 定义处理函数
				handler(newValue, oldValue) {
					// 当chatList长度变化时，自动滚动到底部
					if (newValue) {
						this.scrollToBottom();
					}
				}
			},
			// 监听chatList内容变化（用于流式更新时的滚动）
			chatList: {
				deep: true,
				handler(newList, oldList) {
					// 当消息内容更新时，延迟滚动确保DOM已更新
					this.$nextTick(() => {
						this.scrollToBottom();
					});
				}
			}
		},
		// 组件挂载完成生命周期函数
		mounted() { 
			// 通过refs打开居中显示的dialog组件
			this.$refs.dialog.open('center');
			// 获取当前时间并格式化为HH:MM格式
			let myDate = new Date();
			this.currentDate = (myDate.getHours() + '').padStart(2, '0') + ':' + (myDate.getMinutes() + '').padStart(2, '0');
			// 初始化WebSocket连接
			this.initSocket();
		},
		// 页面卸载前关闭WebSocket连接
		beforeUnmount() {
			if (this.socketTask) {
				this.socketTask.close();
			}
		},
		// 定义组件方法
		methods: {
			// 自动滚动到页面底部
			scrollToBottom() {
				this.$nextTick(() => {
					// 获取聊天区域的高度
					const query = uni.createSelectorQuery().in(this);
					query.select('#test').boundingClientRect(data => {
						if (data) {
							// 滚动到聊天区域底部
							uni.pageScrollTo({
								scrollTop: data.height + data.top,
								duration: 300 // 平滑滚动动画时长
							});
						}
					}).exec();
				});
			},
			
			htmlContent(content) { //转换为markdown 格式显示
				return marked(content);
			},
			// 打开使用说明对话框
			exemptStatement() {
				this.$refs.dialog.open('center');
			},
			// 点击预设问题时调用，发送对应文本
			tapQuestion(item) {
				this.wssend(item.text); // 修改为调用正确的websocket发送方法
			},
			
			// ----- 使用websocket方法
			// 建立 WebSocket 连接
			initSocket() {
				if (this.socketTask) return;

				this.socketTask = uni.connectSocket({
					url: "ws://127.0.0.1:8000/ws/chat",  // 改成你的后端地址
					success: () => {
						console.log("WebSocket 初始化成功");
					}
				});

				this.socketTask.onOpen(() => {
					this.connected = true;
					console.log("WebSocket 已连接");
				});

				this.socketTask.onMessage((res) => {
					try {
						const data = JSON.parse(res.data);
						if (data.token) {
							// 流式追加 token
							let lastIndex = this.chatList.length - 1;
							if (lastIndex >= 0 && this.chatList[lastIndex].role === 'assistant') {
								this.chatList[lastIndex].content += data.token;
							}
							// 收到回复后清除超时定时器和错误状态
							this.clearResponseTimeout();
							this.showConnectionError = false; // 清除连接错误状态
							
							// 流式更新时自动滚动
							this.$nextTick(() => {
								this.scrollToBottom();
							});
						} else if (data.event === "DONE") {
							// 一条完整回答结束，隐藏加载状态和清除超时
							this.showLoading = false;
							this.showTimeoutError = false;
							this.showConnectionError = false; // 清除连接错误状态
							this.clearResponseTimeout();
							let lastIndex = this.chatList.length - 1;
							if (lastIndex >= 0) {
								this.chatList[lastIndex].done = true;
							}
							// 消息完成时确保滚动到底部
							this.scrollToBottom();
						}
					} catch (e) {
						console.error("消息解析失败:", e, res.data);
					}
				});

				this.socketTask.onClose(() => {
					this.connected = false;
					console.log("WebSocket 已关闭");
				});

				this.socketTask.onError((err) => {
					console.error("WebSocket 出错:", err);
					// WebSocket出错时，立即终止"响应中"状态，显示连接错误信息
					this.showLoading = false;
					this.showConnectionError = true;
					this.clearResponseTimeout();
					
					// 3秒后自动隐藏错误信息
					setTimeout(() => {
						this.showConnectionError = false;
					}, 3000);
				});
			},

			// 清除响应超时定时器
			clearResponseTimeout() {
				if (this.timeoutTimer) {
					clearTimeout(this.timeoutTimer);
					this.timeoutTimer = null;
				}
			},
			
			// 设置响应超时定时器
			setResponseTimeout() {
				this.clearResponseTimeout(); // 先清除之前的定时器
				this.timeoutTimer = setTimeout(() => {
					// 超时后隐藏加载状态，显示错误信息
					this.showLoading = false;
					this.showTimeoutError = true;
					console.log('服务器响应超时');
					
					// 3秒后自动隐藏错误信息
					setTimeout(() => {
						this.showTimeoutError = false;
					}, 3000);
				}, this.responseTimeout);
			},

			// 发送用户输入
			async wssend(val) {
				if (!this.connected) {
					this.initSocket();
					await new Promise(resolve => setTimeout(resolve, 500)); // 等待连接
				}

				// 打印当前消息数组并显示加载状态
				console.log(this.messages);
				
				this.showLoading = true;
				this.showTimeoutError = false; // 重置错误状态
				this.showConnectionError = false; // 重置连接错误状态
				
				// 设置响应超时定时器
				this.setResponseTimeout();
				// 创建用户消息对象并添加到聊天列表和消息数组
				let userMessage = {
					role: 'user',
					content: val
				};
				this.chatList.push(userMessage);
				this.messages.push(userMessage);

				// 创建空的助手消息对象并添加到两个数组
				let assistantMessage = {
					role: 'assistant',
					content: ''
				};
				this.chatList.push(assistantMessage);
				this.messages.push(assistantMessage);

				this.socketTask.send({
					data: JSON.stringify({
						message: val,
						history: this.history
					})
				});

				// 把用户输入追加到 history 里
				this.history.push({ role: "user", content: val });
				this.history.push({ role: "assistant", content: "" }); // 等模型返回后填充
			},
			
			// 发送用户问题并清空输入
			sendMsg() {
				if (!this.userQuesion.trim()) {
					uni.showToast({
						title: '请输入问题',
						icon: 'none'
					});
					return;
				}
				// 调用websocket方法
				this.wssend(this.userQuesion);
				this.userQuesion = '';
				this.robotAnswer = '';
				
				// 发送消息后滚动到底部
				this.$nextTick(() => {
					this.scrollToBottom();
				});
			}
		}
	};
</script>

<!-- 声明使用SCSS（Sass）预处理器编写样式 -->
<style lang="scss" scoped>
	// 定义容器类，设置内边距为28rpx（rpx是响应式单位，会根据屏幕宽度自适应）
	.container {
		padding: 28rpx;
		background-color: #ffffff; // 白色背景
		min-height: 100vh;
		// 预留底部导航栏高度（50px = 100rpx），避免输入栏被遮挡
		padding-bottom: 120rpx;
	}

	// 定义导航栏样式：
	.nav {
		height: 80rpx;
		width: 100%;
		background-color: #ffffff;
		display: flex;
		align-items: center;
		position: fixed;
		top: 0;
		left: 0;
		z-index: 999;

		// 导航栏内图片样式
		image {
			margin: 0 20rpx;
			width: 40rpx;
			height: 40rpx;

		}

		// 导航栏内文字样式
		text {
			color: #838383;
			font-size: 40rpx;
		}
	}

	// 定义聊天区域样式
	.chat_area {
		padding-bottom: 200rpx;
		// 设置白色背景
		background-color: #ffffff;
		
		// 当前时间显示样式
		.current_time {
			display: flex;
			justify-content: center;
			font-size: 12px;
			color: #666666;
			margin: 20rpx 0;
		}

		// 左侧和右侧消息框的共同样式 - 移除头像后调整布局
		.left_box,
		.right_box {
			display: flex;
			margin: 20rpx 16rpx; // 减半对话框四周留白
			// 移除最大宽度限制，让内容自适应

			// 消息内容框样式 - 参考图片中的圆润气泡设计，无边框
			.content_box {
				// 根据内容自适应宽度，但设置合理的最大宽度
				max-width: 80%;
				min-width: 80rpx;
				width: fit-content;
				word-wrap: break-word;
				overflow-wrap: break-word;

				.content {
					// 增加内边距，让文字不紧贴对话框边缘
					padding: 32rpx 40rpx;
					// 移除边框和阴影，保持简洁
					border: none;
					box-shadow: none;
					
					// 字体样式调整 - 自定义字体粗细，固定行高
					font-size: 16px !important;
					font-weight: 540 !important; // 调整为540
					line-height: 24px !important; // 固定行高为24px
					color: #333333;
					// 禁用任何可能导致字号变化的属性
					-webkit-text-size-adjust: none !important;
					text-size-adjust: none !important;
					zoom: 1 !important;
					transform: none !important;
					margin: 0;

					// 请求帖子样式
					.post_request {
						color: #666666;
						display: flex;
						flex-direction: column;
						margin: 0;
						
						// 每个可点击问题项的样式
						view {
							margin: 6rpx 0; // 稍微增加间距
							padding: 12rpx 20rpx; // 增加内边距
							border-radius: 16rpx;
							
							// 可点击文字的样式
							.active {
								color: #007AFF;
								cursor: pointer;
								font-weight: 540 !important; // 保持自定义字体粗细
								line-height: 24px !important; // 固定行高
								// 鼠标悬停效果
								&:hover {
									background-color: rgba(0, 122, 255, 0.1);
									color: #0056CC;
								}
								
								// 活动状态样式（按下时）
								&:active {
									background-color: rgba(0, 122, 255, 0.2);
									opacity: 0.8;
								}
							}
						}
					}
				    
				    // 强制所有HTML内容元素使用统一的字体样式
				    *, p, div, span, text, view {
				    	font-size: 16px !important;
				    	line-height: 24px !important;
				    	font-weight: 540 !important;
				    	-webkit-text-size-adjust: none !important;
				    	text-size-adjust: none !important;
				    	zoom: 1 !important;
				    	transform: none !important;
				    	margin: 0 !important;
				    }
				    
				    h1, h2, h3, h4, h5, h6 {
				    	font-size: 16px !important;
				    	line-height: 24px !important;
				    	font-weight: 540 !important;
				    	margin: 0 !important;
				    }
				    
				    li, ul, ol {
				    	font-size: 16px !important;
				    	line-height: 24px !important;
				    	font-weight: 540 !important;
				    	margin: 0 !important;
				    }
				    
				    strong, b {
				    	font-size: 16px !important;
				    	line-height: 24px !important;
				    	font-weight: 540 !important;
				    }
				    
				    em, i {
				    	font-size: 16px !important;
				    	line-height: 24px !important;
				    	font-weight: 540 !important;
				    	font-style: normal !important;
				    }
				    
				    code, pre {
				    	font-size: 16px !important;
				    	line-height: 24px !important;
				    	font-weight: 540 !important;
				    	font-family: inherit !important;
				    }
				}
			}
		}
		
		// 左侧消息框（机器人）
		.left_box {
			justify-content: flex-start;
			
			.content_box {
				background-color: #e5e5ea !important;
				color: #000000 !important;
				border-radius: 44rpx 44rpx 44rpx 8rpx !important;
			}
		}
		
		// 右侧消息框（用户）
		.right_box {
			justify-content: flex-end;
			
			.content_box {
				background: linear-gradient(180deg, #4A9EFF 0%, #7BB8FF 100%) !important;
				color: #ffffff !important;
				margin-left: auto;
				border-radius: 44rpx 44rpx 8rpx 44rpx !important;
				
				.content {
					color: #ffffff !important;
					
					*, p, div, span, text, view {
						color: #ffffff !important;
					}
				}
			}
		}
		
		// 屏幕适配
		@media (min-width: 720px) and (max-width: 1199px) {
			.left_box .content_box, 
			.right_box .content_box {
				max-width: 60%;
			}
			.left_box,
			.right_box {
				margin: 20rpx 24rpx;
			}
		}
		
		@media (min-width: 1200px) {
			.left_box .content_box, 
			.right_box .content_box {
				max-width: 50%;
			}
			.left_box,
			.right_box {
				margin: 20rpx 32rpx;
			}
		}
	}

	// 错误信息提示样式
	.error_message {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 20rpx;
		margin: 20rpx;
		background-color: #fff2f0;
		border: 1rpx solid #ffccc7;
		border-radius: 16rpx;
		
		text {
			color: #ff4d4f;
			font-size: 14px;
		}
	}

	// 底部输入栏样式
	.input_tab {
		background-color: #ffffff;
		width: 100%;
		position: fixed;
		bottom: 100rpx; // 距离底部100rpx，避免被导航栏遮挡
		left: 0;
		display: flex;
		flex-direction: column;
		padding: 16rpx 0;
	}

	// 声明文字样式
	.statement {
		margin: 0 auto 12rpx auto;
		font-size: 12px;
		color: #999999;
		text-align: center;

		text {
			color: #007AFF;
			text-decoration: underline;
		}
	}
	
	// 输入组件容器样式
	.input_com {
		display: flex;
		justify-content: space-between;
		padding: 16rpx 30rpx;
		gap: 16rpx;

		// 左侧输入区域样式
		.left {
			flex: 1;
			border: 2rpx solid #e0e0e0;
			display: flex;
			align-items: center;
			background-color: #ffffff;
			border-radius: 48rpx;
			padding: 0 8rpx;
			min-height: 80rpx;

			// 输入框内图标样式
			image {
				width: 32rpx;
				height: 32rpx;
				margin: 0 24rpx;
				opacity: 0.6;
			}
			
			// 输入框样式
			input {
				width: 100%;
				font-size: 16px;
				background-color: transparent;
				border: none;
				outline: none;
				padding: 20rpx 0;
			}
		}
		
		// 发送按钮样式
		.send_btn {
			width: 80rpx;
			height: 80rpx;
			padding: 0;
			color: #ffffff;
			border-radius: 40rpx;
			background: linear-gradient(180deg, #4A9EFF 0%, #7BB8FF 100%);
			border: none;
			flex-shrink: 0;
			display: flex;
			align-items: center;
			justify-content: center;
			font-size: 14px;
			font-weight: 500;
			box-shadow: none;
			
			&:active {
				transform: scale(0.95);
				opacity: 0.8;
			}
		}
	}
</style>