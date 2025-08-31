<template>
	<!-- 页面根容器 -->
	<view class="container">
		<!-- 背景图片和遮罩 -->
		<image class="bg" src="../../static/img/home_bg.png" mode="aspectFill"></image>
		<view class="overlay"></view>
		
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
			<view v-if="showLoading && !showTimeoutError && !showConnectionError" class="loading-container">
				<u-loading-icon text="响应中，请稍后..." textSize="16" :show="true"></u-loading-icon>
			</view>
			
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
			<!-- 服务说明 - 移到输入框上方 -->
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
	import statement from "../../components/statement.vue";
	import { marked } from "marked";

	export default {
		components: {
			statement
		},
		data() {
			return {
				apiBaseUrl: 'http://192.168.20.234:8000', // 开发时请务必替换为您的电脑IP地址
				socketTask: null,
				isConnected: false,
				
				showLoading: false, // 控制“响应中”的加载动画
				chatList: [],
				userQuesion: '',
				currentDate: '',
				postRequest: [{
					id: 1,
					text: '把空调温度调低一点'
				}, {
					id: 2,
					text: '打开卧室灯'
				}, {
					id: 3,
					text: '显示当前气温'
				}],
			};
		},
		onLoad() {
			this.initWebSocket();
		},
		onUnload() {
			this.closeWebSocket();
		},
		watch: {
			// 每次chatList变化都滚动到底部
			chatList: {
				handler() { this.scrollToBottom(); },
				deep: true
			}
		},
		mounted() {
			// ... (mounted中其他代码不变)
		},
		methods: {
			initWebSocket() {
				const token = uni.getStorageSync("token");
				if (!token) {
					uni.showToast({ title: '请先登录', icon: 'none' });
					return;
				}
				// 将 http:// 替换为 ws://
				const wsUrl = `${this.apiBaseUrl.replace('http', 'ws')}/api/v1/ai/ws/chat?token=${token}`;

				this.socketTask = uni.connectSocket({
					url: wsUrl,
					success: () => { console.log("WebSocket 开始连接..."); }
				});

				this.socketTask.onOpen(() => {
					this.isConnected = true;
					console.log("✅ WebSocket 连接成功");
				});

				this.socketTask.onMessage((res) => {
					const data = JSON.parse(res.data);
					let lastMessage = this.chatList[this.chatList.length - 1];

					// 确保有一个AI的回复消息占位符
					if (!lastMessage || lastMessage.role !== 'assistant') return;

					switch (data.type) {
						case 'text':
							// 核心：流式追加文本
							lastMessage.content += data.content;
							break;
						case 'status':
							// 显示状态更新，例如“正在解析指令...”
							lastMessage.content = data.content;
							break;
						case 'result':
							// 显示最终的执行结果
							lastMessage.content = data.content;
							break;
						case 'error':
							lastMessage.content = `[错误] ${data.content}`;
							this.showLoading = false;
							break;
						case 'done':
							// 一次问答结束，隐藏加载动画
							this.showLoading = false;
							this.scrollToBottom(); // 确保最终滚动到底部
							break;
					}
				});

				this.socketTask.onError((err) => {
					this.isConnected = false;
					this.showLoading = false;
					console.error("WebSocket 连接发生错误", err);
				});

				this.socketTask.onClose(() => {
					this.isConnected = false;
					this.showLoading = false;
					console.log("WebSocket 连接已关闭");
					// 可以加入断线重连逻辑
				});
			},

			closeWebSocket() {
				if (this.socketTask) {
					this.socketTask.close();
				}
			},
			
			sendMsg() {
				if (!this.userQuesion.trim()) return;

				if (!this.isConnected) {
					uni.showToast({ title: '连接已断开，正在尝试重连...', icon: 'none' });
					this.initWebSocket();
					return;
				}
				
				// 1. 立即将用户自己的消息推入列表
				this.chatList.push({
					role: 'user',
					content: this.userQuesion
				});

				// 2. 立即创建一个空的AI回复占位符
				this.chatList.push({
					role: 'assistant',
					content: '' // 初始为空，等待流式数据填充
				});
				
				// 3. 显示加载状态
				this.showLoading = true;
				this.scrollToBottom();
				
				// 4. 通过WebSocket发送消息到后端
				this.socketTask.send({
					data: this.userQuesion,
					success: () => {
						this.userQuesion = ''; // 发送成功后清空输入框
					},
					fail: (err) => {
						uni.showToast({ title: '消息发送失败', icon: 'none'});
						console.error('WebSocket发送失败', err);
						this.showLoading = false;
					}
				});
			},

			tapQuestion(item) {
				this.userQuesion = item.text;
				this.sendMsg();
			},
			htmlContent(content) {
				return marked(content);
			},
			// ... (其他方法如 scrollToBottom, exemptStatement 保持不变)
		}
	};
</script>

<style lang="scss" scoped>
	// 容器样式 - 使用绝对定位避免滚动问题
	.container {
		position: fixed;
		top: 0;
		left: 0;
		width: 100vw;
		height: 100vh;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	// 背景图片 - 固定背景，不随页面滚动
	.bg {
		position: fixed;
		width: 100vw;
		height: 100vh;
		object-fit: cover;
		object-position: center;
		z-index: 1;
		top: 0;
		left: 0;
	}

	// 遮罩层 - 固定遮罩
	.overlay {
		position: fixed;
		width: 100vw;
		height: 100vh;
		background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6));
		z-index: 2;
		top: 0;
		left: 0;
	}

	// 聊天区域样式 - 修改为绝对定位，底部距离280rpx
	.chat_area {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 220rpx; // 设置底部距离为280rpx
		z-index: 3;
		padding: 40rpx 28rpx 40rpx 28rpx; // 调整底部padding，避免内容贴边
		overflow-y: auto;
		overflow-x: hidden; // 防止横向滚动
		
		// 滚动条样式优化（仅在支持的浏览器中生效）
		&::-webkit-scrollbar {
			width: 4rpx;
		}
		
		&::-webkit-scrollbar-track {
			background: rgba(255, 255, 255, 0.1);
			border-radius: 2rpx;
		}
		
		&::-webkit-scrollbar-thumb {
			background: rgba(255, 255, 255, 0.3);
			border-radius: 2rpx;
		}
		
		&::-webkit-scrollbar-thumb:hover {
			background: rgba(255, 255, 255, 0.5);
		}
		
		// 当前时间显示样式
		.current_time {
			display: flex;
			justify-content: center;
			font-size: 12px;
			color: rgba(255, 255, 255, 0.8);
			margin: 20rpx 0;
		}

		// 左侧和右侧消息框的共同样式
		.left_box,
		.right_box {
			display: flex;
			margin: 20rpx 16rpx;

			// 消息内容框样式 - 使用毛玻璃效果
			.content_box {
				max-width: 80%;
				min-width: 80rpx;
				width: fit-content;
				word-wrap: break-word;
				overflow-wrap: break-word;

				.content {
					padding: 32rpx 40rpx;
					border-radius: 30rpx;
					box-shadow: 0 15rpx 40rpx rgba(0, 0, 0, 0.2);
					backdrop-filter: blur(20rpx);
					
					// 字体样式调整
					font-size: 16px !important;
					font-weight: 540 !important;
					line-height: 24px !important;
					-webkit-text-size-adjust: none !important;
					text-size-adjust: none !important;
					zoom: 1 !important;
					transform: none !important;
					margin: 0;

					// 请求帖子样式 - 去除示例问题的背景
					.post_request {
						color: #666666;
						display: flex;
						flex-direction: column;
						margin: 0;
						
						view {
							margin: 6rpx 0;
							padding: 12rpx 20rpx;
							border-radius: 16rpx;
							background: transparent;
							
							.active {
								color: #007AFF;
								cursor: pointer;
								font-weight: 540 !important;
								line-height: 24px !important;
								
								&:hover {
									background-color: rgba(0, 122, 255, 0.1);
								}
								
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
		
		// 左侧消息框（机器人） - 使用更清亮的毛玻璃效果
		.left_box {
			justify-content: flex-start;
			
			.content_box {
				background: rgba(255, 255, 255, 0.85) !important;
				color: #333333 !important;
				border-radius: 44rpx 44rpx 44rpx 8rpx !important;
				border: 1rpx solid rgba(255, 255, 255, 0.5);
				backdrop-filter: blur(15rpx);
			}
		}
		
		// 右侧消息框（用户） - 仿照机器人对话框调整
		.right_box {
			justify-content: flex-end;
			
			.content_box {
				background: linear-gradient(180deg, #4A9EFF 0%, #7BB8FF 100%) !important;
				color: #ffffff !important;
				margin-left: auto;
				border-radius: 44rpx 44rpx 8rpx 44rpx !important;
				border: 1rpx solid rgba(255, 255, 255, 0.5);
				backdrop-filter: blur(15rpx);
				
				.content {
					color: #ffffff !important;
					
					*, p, div, span, text, view {
						color: #ffffff !important;
					}
				}
			}
		}
	}

	// 加载提示容器样式
	.loading-container {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 20rpx 0;
		margin: 20rpx 0;
		flex-shrink: 0; // 防止被压缩
	}

	// 错误信息提示样式 - 确保在聊天区域内显示
	.error_message {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 20rpx;
		margin: 20rpx 0; // 改为上下边距，避免左右边距影响布局
		background: rgba(255, 242, 240, 0.9);
		border: 1rpx solid rgba(255, 204, 199, 0.8);
		border-radius: 16rpx;
		backdrop-filter: blur(10rpx);
		max-width: 100%; // 确保不超出聊天区域
		box-sizing: border-box;
		flex-shrink: 0; // 防止被压缩
		
		text {
			color: #ff4d4f;
			font-size: 14px;
			text-align: center;
		}
	}

	// 底部输入栏样式 - 调整布局顺序
	.input_tab {
		position: absolute;
		bottom: 80rpx;
		left: 0;
		right: 0;
		height: 240rpx;
		z-index: 10;
		background: transparent;
		display: flex;
		flex-direction: column;
		justify-content: flex-end; // 改为底部对齐
		padding: 20rpx 0;
		box-sizing: border-box;
	}

	// 声明文字样式 - 调整边距，现在在输入框上方
	.statement {
		margin: 0 auto 16rpx auto; // 调整边距，底部留给输入框空间
		font-size: 12px;
		color: rgba(255, 255, 255, 0.8);
		text-align: center;

		text {
			color: #FFFFFF;
			text-decoration: underline;
			font-weight: 500;
		}
	}
	
	// 输入组件容器样式
	.input_com {
		display: flex;
		justify-content: space-between;
		padding: 16rpx 30rpx;
		gap: 16rpx;

		// 左侧输入区域样式 - 使用毛玻璃效果
		.left {
			flex: 1;
			border: 2rpx solid rgba(255, 255, 255, 0.3);
			display: flex;
			align-items: center;
			background: rgba(255, 255, 255, 0.15);
			backdrop-filter: blur(10rpx);
			border-radius: 48rpx;
			padding: 0 8rpx;
			min-height: 80rpx;

			// 输入框内图标样式
			image {
				width: 32rpx;
				height: 32rpx;
				margin: 0 24rpx;
				opacity: 0.8;
			}
			
			// 输入框样式
			input {
				width: 100%;
				font-size: 16px;
				background-color: transparent;
				border: none;
				outline: none;
				padding: 20rpx 0;
				color: #FFFFFF;
				
				&::placeholder {
					color: rgba(255, 255, 255, 0.7);
				}
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
			box-shadow: 0 15rpx 40rpx rgba(0, 0, 0, 0.2);
			
			&:active {
				transform: scale(0.95);
				opacity: 0.8;
			}
		}
	}
</style>