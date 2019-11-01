#!/usr/bin/env bash

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
plain='\033[0m'

cur_dir=$(pwd)

# check root
[[ $EUID -ne 0 ]] && echo -e "${red}错误：${plain} 必须使用 root 用户运行此脚本！\n" && exit 1

# check os
if [[ -f /etc/redhat-release ]]; then
  release="centos"
elif cat /etc/issue | grep -Eqi "debian"; then
  release="debian"
elif cat /etc/issue | grep -Eqi "ubuntu"; then
  release="ubuntu"
elif cat /etc/issue | grep -Eqi "centos|red hat|redhat"; then
  release="centos"
elif cat /proc/version | grep -Eqi "debian"; then
  release="debian"
elif cat /proc/version | grep -Eqi "ubuntu"; then
  release="ubuntu"
elif cat /proc/version | grep -Eqi "centos|red hat|redhat"; then
  release="centos"
else
  echo -e "${red}未检测到系统版本，请联系脚本作者！${plain}\n" && exit 1
fi

os_version=""

# os version
if [[ -f /etc/os-release ]]; then
  os_version=$(awk -F'[= ."]' '/VERSION_ID/{print $3}' /etc/os-release)
fi
if [[ -z "$os_version" && -f /etc/lsb-release ]]; then
  os_version=$(awk -F'[= ."]+' '/DISTRIB_RELEASE/{print $2}' /etc/lsb-release)
fi

if [[ x"${release}" == x"centos" ]]; then
  if [[ ${os_version} -le 6 ]]; then
    echo -e "${red}请使用 CentOS 7 或更高版本的系统！${plain}\n" && exit 1
  fi
elif [[ x"${release}" == x"ubuntu" ]]; then
  if [[ ${os_version} -lt 16 ]]; then
    echo -e "${red}请使用 Ubuntu 16 或更高版本的系统！${plain}\n" && exit 1
  fi
elif [[ x"${release}" == x"debian" ]]; then
  if [[ ${os_version} -lt 8 ]]; then
    echo -e "${red}请使用 Debian 8 或更高版本的系统！${plain}\n" && exit 1
  fi
fi

install_py() {
  if [[ x"${release}" == x"centos" ]]; then
    yum install python36 python36-devel python3-pip -y
  else
    apt install python3 python3-pip python3-dev -y
  fi
  if [[ $? -ne 0 ]]; then
    echo -e "${red}python3 安装失败，请查看错误信息${plain}"
    exit 1
  fi
  pip3 install virtualenv
  if [[ $? -ne 0 ]]; then
    echo -e "${red}pip3 安装失败，请查看错误信息${plain}"
    exit 1
  fi
}

install_base() {
  if [[ x"${release}" == x"centos" ]]; then
    yum update -y
    yum install wget curl tar gcc -y
  else
    apt update
    apt upgrade -y
    apt install wget curl tar gcc -y
  fi
  install_py
}

install_v2ray() {
  echo -e "${green}开始安装 or 升级 v2ray${plain}"
  bash <(curl -L -s https://install.direct/go.sh)
  if [[ $? -ne 0 ]]; then
    echo -e "${red}v2ray 安装或升级失败，请检查错误信息${plain}"
    exit 1
  fi
  systemctl enable v2ray
  systemctl start v2ray
}

close_firewall() {
  if [[ x"${release}" == x"centos" ]]; then
    systemctl stop firewalld
    systemctl disable firewalld
  elif [[ x"${release}" == x"ubuntu" ]]; then
    ufw disable
  elif [[ x"${release}" == x"debian" ]]; then
    iptables -P INPUT ACCEPT
    iptables -P OUTPUT ACCEPT
    iptables -P FORWARD ACCEPT
    iptables -F
  fi
}

install_v2-ui() {
  if [[ -e /usr/local/v2-ui/v2-ui ]]; then
    rm /usr/local/v2-ui/v2-ui -rf
  fi

  if [[ ! -e /usr/local/v2-ui/ ]]; then
    /usr/local/bin/virtualenv -p python3 /usr/local/v2-ui/
  fi
  source /usr/local/v2-ui/bin/activate

  systemctl stop v2-ui
  cd /usr/local/v2-ui/
  last_version=$(curl -Ls "https://api.github.com/repos/sprov065/v2-ui/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
  echo -e "检测到 v2-ui 最新版本：${last_version}，开始安装"
  wget -N --no-check-certificate -O /usr/local/v2-ui/v2-ui.tar.gz https://github.com/sprov065/v2-ui/archive/${last_version}.tar.gz
  if [[ $? -ne 0 ]]; then
    echo -e "${red}下载 v2-ui 失败，请确保你的服务器能够下载 Github 的文件，如果多次安装失败，请参考手动安装教程${plain}"
    exit 1
  fi
  tar zxvf v2-ui.tar.gz
  rm v2-ui.tar.gz -f
  mv v2-ui-${last_version} v2-ui
  cd v2-ui
  pip3 install -r requirements.txt
  if [[ $? -ne 0 ]]; then
    echo -e "${red}安装 python 依赖库失败，请检查错误信息${plain}"
    exit 1
  fi
  cp -f v2-ui.service /etc/systemd/system/
  systemctl daemon-reload
  systemctl enable v2-ui
  systemctl start v2-ui
  echo -e "${green}v2-ui v${last_version}${plain} 安装完成，面板已启动，"
  echo -e ""
  echo -e "如果是全新安装，默认网页端口为 ${green}65432${plain}，用户名和密码默认都是 ${green}admin${plain}"
  echo -e "请自行确保此端口没有被其他程序占用，${yellow}并且确保 65432 端口已放行，卖 VPS 的商家的网页面板上的防火墙也要放行，否则无法访问${plain}"
  echo -e ""
  echo -e "如果是更新面板，则按你之前的方式访问面板"
  echo -e ""
  curl -o /usr/bin/v2-ui -Ls https://raw.githubusercontent.com/sprov065/v2-ui/master/v2-ui.sh
  chmod +x /usr/bin/v2-ui
  echo -e "v2-ui 管理脚本使用方法: "
  echo -e "----------------------------------------------"
  echo -e "v2-ui              - 显示管理菜单 (功能更多)"
  echo -e "v2-ui start        - 启动 v2-ui 面板"
  echo -e "v2-ui stop         - 停止 v2-ui 面板"
  echo -e "v2-ui restart      - 重启 v2-ui 面板"
  echo -e "v2-ui status       - 查看 v2-ui 状态"
  echo -e "v2-ui enable       - 设置 v2-ui 开机自启"
  echo -e "v2-ui disable      - 取消 v2-ui 开机自启"
  echo -e "v2-ui log          - 查看 v2-ui 日志"
  echo -e "v2-ui update       - 更新 v2-ui 面板"
  echo -e "v2-ui install      - 安装 v2-ui 面板"
  echo -e "v2-ui uninstall    - 卸载 v2-ui 面板"
  echo -e "----------------------------------------------"
}

echo -e "${green}开始安装${plain}"
install_base
install_v2ray
install_v2-ui
