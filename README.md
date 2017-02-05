# 基于ssh反向代理实现的远程协助

通过ssh反向代理实现远程协助，并提供了相关代码。    		
可满足web开启远程协助功能后，维护人员能够通过ssh和http登录客户机器（包括在nat环境下）			
* web开启该功能后，ssh才能登录；     			
* 通过标识能够区分不同的机器；     		
* 能够穿nat；		

环境：
CentOS 6.5_x64
