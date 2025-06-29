**本次实验实现了vmware中对linux系统ubuntu20.04安装、pycharm
安装、python环境配置**

本次实验采用vmware虚拟机安装ubunt
20.04版本进行。（还可以采取**双系统**或**wsL2**进行实验）

1.首先进入**vmware**软件点击左上角文件\--\>\>\>新建虚拟机

![](D:\linux_install_img/media/image1.png){width="5.764583333333333in"
height="4.483333333333333in"}

![](D:\linux_install_img/media/image2.png){width="5.013888888888889in"
height="4.729166666666667in"}

2.  这一步直接勾选**典型**，点击下一步

    ![](D:\linux_install_img/media/image3.png){width="4.916666666666667in"
    height="4.666666666666667in"}

3.  接下来填写一个名字跟密码，这里的密码建议填写一个**简单**的密码，方便记忆和使用。

    ![](D:\linux_install_img/media/image4.png){width="5.006944444444445in"
    height="4.673611111111111in"}

    ![](D:\linux_install_img/media/image5.png){width="5.020833333333333in"
    height="4.701388888888889in"}

4.  这里建议修改路径到**D盘**，一般D盘磁盘空间充足，C盘内存小会影响电脑运行速度。

    ![](D:\linux_install_img/media/image6.png){width="5.027777777777778in"
    height="4.701388888888889in"}

5.  这里建议磁盘大小为**40-80G**,磁盘空间分配太小会导致后续一些大型实验结果无法保存，且不会导致主机内存受到影响。然后勾选**将虚拟磁盘存储为单个文件**。

    ![](D:\linux_install_img/media/image7.png){width="4.979166666666667in"
    height="4.75in"}

6.  这里可以根据自己的电脑配置再具体调整参数，内存一般是4-8GB即可，处理器可以根据自己的电脑来，我这里是i7-13700H（共20线程），所以给的3\*2=6vCPU\
    给主机留 14 线程余量。

    ![](D:\linux_install_img/media/image8.png){width="5.763888888888889in"
    height="2.4069444444444446in"}

    ![](D:\linux_install_img/media/image9.png){width="5.761805555555555in"
    height="6.468055555555556in"}

7.  显示器这里勾选**加速3D图形，**显存一般默认的4GB。这里的打印机一般用不到，可以点击左侧下面的移除进行移除，需要时可再修改增加。

8.  这里点击**完成**即可。

    ![](D:\linux_install_img/media/image10.png){width="4.888888888888889in"
    height="4.597222222222222in"}

    ![](D:\linux_install_img/media/image11.png){width="5.752777777777778in"
    height="3.397222222222222in"}

9.  到这里一台新的虚拟机就搭建成功了，点击**开启虚拟机**就行。

    ![](D:\linux_install_img/media/image12.png){width="5.750694444444444in"
    height="3.104861111111111in"}

10. 进来之后一般是正常联网的，如果有问题，请检查上一步是否勾选NAT模式

11. 另外，建议使用vmware时连接键盘，这样操作比较方便。

12. 如果使用界面大小不舒服，可以在setting中进行设置\-\-\-\--\>\>\>\>\>display中修改分辨率

    ![](D:\linux_install_img/media/image13.png){width="5.761111111111111in"
    height="4.888194444444444in"}

13. Date&Time中设置时间地区，Regions&languages中设置语言和地区（只要时间一样就行，即就是时区
    CST（UTC+8）即可

14. 拼音输入法。然后在manage installed
    languages添加Chinesse(simplified)，然后在language行点击后选择汉语，再点击下面图片中的设置键，进入找到对应的中文拼音就行。

15. 再重启即可切换至中文。

    ![](D:\linux_install_img/media/image14.png){width="5.764583333333333in"
    height="4.856944444444444in"}

16. 还有就是下载pycharm，直接上网站上找一个用命令行下载的链接就行，一般都是x86的下面的.deb格式就行，下载后正常打开就行。

17. 在配置解释器的时候先将自己的环境路径搞清楚就可以在pycharm路径下找这个解释器了。
