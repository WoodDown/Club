#!/usr/bin/env bash
. ./secret.sh

set -ex

# 系统设置
apt-get install -y zsh curl ufw
# sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 465
ufw default deny incoming
ufw default allow outgoing
ufw status verbose
ufw -f enable

# redis 需要 ipv6
sysctl -w net.ipv6.conf.all.disable_ipv6=0

# 安装过程中选择默认选项，这样不会弹出 libssl 确认框
export DEBIAN_FRONTEND=noninteractive

# 安装依赖
apt-get install -y git supervisor nginx python3-pip mysql-server redis-server
pip3 install jinja2 flask gevent gunicorn pymysql flask_sqlalchemy flask_mail marrow.mailer redis celery

# 删除测试用户和测试数据库
# 删除测试用户和测试数据库并限制关闭公网访问
mysql -u root -p$SQLPWD -e "DELETE FROM mysql.user WHERE User='';"
mysql -u root -p$SQLPWD -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -u root -p$SQLPWD -e "DROP DATABASE IF EXISTS test;"
mysql -u root -p$SQLPWD -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
# 设置密码并切换成密码验证
mysql -u root -p$SQLPWD -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$SQLPWD';"

# 删掉 nginx default 设置
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-available/default

# 不要在 sites-available 里面放任何东西
cp /var/www/club/club.nginx /etc/nginx/sites-enabled/club
chmod -R o+rwx /var/www/club

# 配置文件
cp /var/www/club/club.conf /etc/supervisor/conf.d/club.conf
cp /var/www/club/celery.conf /etc/supervisor/conf.d/celery.conf

# 初始化
cd /var/www/club
python3 reset.py

# 重启服务器
service supervisor restart
service nginx restart

echo 'succsss'
echo 'ip'
hostname -I
#todo ssl auto yes
