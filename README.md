# 部署

## 项目依赖
* <a href='https://github.com/wodfan/icehole'>中间件</a>
* <a href='https://github.com/wodfan/hichao_utils'>hichao_util</a>

##虚拟环境配置

### 安装virtualenv
* sudo pip install virtualenv
* 如果本机没有安装pip，需要先安装pip，<a href='https://pypi.python.org/pypi/pip'>点击这里</a>下载安装

### 安装virtualenvwrapper
* sudo pip install virtualenvwrapper
* <a href='http://virtualenvwrapper.readthedocs.org/en/latest/install.html'>点击这里</a>查看详细配置

### 新建虚拟环境
* mkvirtualenv env

### 切换到虚拟环境
* workon env

## 安装

### 安装中间件客户端
1. git clone git@github.com:wodfan/icehole.git
2. cd icehole
3. ./setup client

### 安装新版中间件客户端
1. cd icehole
2. git clean -d -f
3. git checkout ice
4. git clean -d -f
5. ice_client=[local | dev | beta | release] python setup_client.py install   (local/dev等为要使用哪个环境的中间件)


### 安装hichao_utils
1. git clone git@github.com:wodfan/hichao_utils.git
2. cd hichao_utils
3. python setup.py install

### 安装hichao_backend
1. cd hichao_backend
2. sh scripts/install.sh

安装期间可能会遇到各种依赖不存在的问题，解决依赖后重新执行install脚本即可。

## 修改配置

线上部署可以直接跳过这一段

### uwsgi配置

存放于项目根目录的ini文件，线上环境用的production.ini，如果非线上环境可以复制一份，做相应的修改启动即可。

相关参数：

* `processes`：进程个数
* `socket`：服务监听的端口
* `stats`：服务状态获取端口
* `listen`：允许接入的请求队列大小
* `daemonize`：日志路径
* `touch-logreopen`：刷新日志文件路径标记文件路径（touch该文件会导致uwsgi刷新日志路径fd）
* `log-reopen`：是否支持touch-logreopen配置
* `pidfile`：pid路径
* `procname`：进程名
* `env`：环境变量

更多参数可以参照<a href='http://uwsgi-docs.readthedocs.org/en/latest/Options.html'>uwsgi配置说明</a>

### 项目配置
<font color='red'>注：非线上环境，请务必更改或新加以下相关配置！</font>

文件存放于`hichao/base/config`，`__init__.py`为通用配置，所有环境都一致；另有与<font color='red'>uwsgi配置中env指定的`thrift_stage`变量相匹配的同名py配置文件</font>，项目启动时会自动加载相应的配置。线上环境用的`yanjiao.py`，非线上环境可以复制一份做相应修改。<font color='red'>新建的配置文件名须与uwsgi配置文件中env指定的thrift_stage变量保持一致</font>。

相关参数：

* `MYSQL_USER`：mysql用户名
* `MYSQL_PASSWD`：mysql密码
* `MYSQL_HOST`：mysql ip
* `MYSQL_PORT`：mysql端口
* `MYSQL_SLAVE_*`与`MYSQL_*`类似，指代mysql从库
* `ECSHOP_MYSQL_*`与`MYSQL_*`类似，指代商城mysql主库
* `ECSHOP_MYSQL_SLAVE_*`与`MYSQL_*`类似，指代商城mysql从库
* `REDIS_CONFIG`与`REDIS_SLAVE_CONFIG`：token验证使用的redis，<font color='red'>需要与token验证的中间件保持一致</font>
* `COLLECTION_REDIS_CONFIG`与`COLLECTION_REDIS_SLAVE_CONFIG`：用户收藏使用的redis，<font color='red'>需要网站与APP保持一致</font>
* `SHORTY_REDIS_CONF`：短链服务使用的redis，<font color='red'>需要与短链服务的中间件保持一致</font>
* `CELERY_BROKER_URL`：CELERY异步执行任务的队列redis
* `SHOP_URL_DOMAIN`：需要调用的`商城接口`域名，<font color='red'>非线上环境需要更改为相应的域名</font>
* `ORDER_SHOP_URL_DOMAIN`：需要调用的`订单相关接口`域名，<font color='red'>非线上环境需要更改为相应的域名</font>
* `API2_URL_DOMAIN`：需要调用的`API接口`域名，<font color='red'>非线上环境需要更改为相应的域名</font>
* `H5_URL_DOMAIN`：需要调用的`H5页面`相关的地址域名，<font color='red'>非线上环境需要更改为相应的域名</font>
* `WEB_URL_DOMAIN`：需要调用的`网页`相关的地址域名，<font color='red'>非线上环境需要更改为相应的域名</font>

### CDN配置

文件存放于`hichao/base/config/CDN.py`，不同业务使用的CDN不同。

MXYC段为<font color='red'>未</font>保存到fastdfs的图片CDN域名；MXYC_SKU段为存到fastdfs上的图片CDN域名；MXYC_FORUM段为社区用户上传图片CDN域名。

### 缓存配置

<font color='red'>注：非线上环境，请务必更改或新加相关缓存配置！</font>

文件存放于`hichao/base/config/redis_conf/`目录下，有与<font color='red'>uwsgi配置中procname相对应的文件，命名方式为"{procname}.py"</font>。手动指定可以参照`api2_notic.py`文件。

相关参数：

* `USE_LOCAL_CACHE`：是否要使用本地进程内缓存，0为不使用，1为使用
* `REDIS_CACHE_CONFIG_LIST`：redis缓存配置

## 启动

### 启动服务

* sh scripts/start.sh {uwsgi_conf}.ini
* uwsgi_conf即uwsgi配置项中的相关ini配置文件

### 停止服务

* sh scripts/stop.sh {uwsgi_conf}.ini

### 重启服务

* sh scripts/restart.sh {uwsgi_conf}.ini

## 其他相关脚本

### crontab相关

文件位于项目根目录，`crontab.conf`文件

* `0 4 * * * /usr/sbin/logrotate -f -s /tmp/logrotate.status /home/api2/hichao_backend/scripts/logrotate` 日志切分，每天凌晨4点执行，<font color='red'>如果uwsgi配置中日志路径有变更，需要在scripts/logrotate中做相应更改</font>
* `20 * * * * /home/api2/env/bin/python /home/api2/hichao_backend/hichao/publish/crontab/publish_hour.py >> /tmp/crontab.log` 明星图发布，每小时的20分执行
* 其余为旧的业务相关定时脚本，现在没用了

使用方法：

因为明星图发布只需要一台服务器执行即可，所以是注释状态，如果全新部署，需要把注释去掉。然后执行`crontab crontab.conf`

### supervisor相关

文件位于scripts文件夹，以supervisor开头相关的配置文件。

* `supervisor_hot_staruser_img.conf`：APP中社区教程达人列表图片更新脚本
* `supervisor_sync_user_post.conf`：用户发、回帖异步后续任务脚本

如果为非线上环境，需要更改相关supervisor配置里相关的日志路径、启动用户等配置，相关配置可以参照<a href='http://supervisord.org/configuration.html'>supervisor配置</a>

### 明星图更新rpc服务

文件位于`hichao/publish/crontab/update_rpc_server.py`，该脚本用于编辑后台调用，当明星图有变更时，调用该rpc，会重新同步相关的明星图及单品数据，并更新缓存。

<font color='red'>服务启动前需要更改文件内的ip地址为服务器当前内网ip，端口做相应变更。</font>

然后在项目根目录执行：

* sh serv_update_rpc.sh

