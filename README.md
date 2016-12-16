#FPS Tool

##实现需求：
动画FPS测试，自动操作（无需手动操作）。

直接运行FPStest.py即可，按需添加参数，参数说明参见下方脚本说明。

##脚本说明：
1. 脚本运行格式：FPStest.py [-o \<LR, UD, DU>][-c \<count>][-m \<method>]
2. 参数说明：
	* -o：操作类型，只有三种类型，LR（左右滑动）、UD（上下滑动）、DU（下上滑动）；
	* -c：测试次数，默认30次；
	* -m：测试方法，gfxinfo、surface两种方法选择，默认为gfxinfo；
	* -h：帮助信息。
3. 脚本原理：
	* 通过gfxinfo或SurfaceFlinger获取每帧耗时用以计算FPS，如选择gfxinfo方法测试，需打开被测设备的“GPS呈现分析”开关;
	* 执行操作时每秒计算一次动画帧率，并在终端上输出计算，并于操作脚本执行完后计算最终平均FPS、丢帧率；
	* 建议选用gfxinfo方式进行测试，如gfxinfo无法取值可选用surfaceFlinger方式测试；
	* 结果均在终端输出，无保留本地文件。