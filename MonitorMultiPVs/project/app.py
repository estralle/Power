 
 

# app.py
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import epics
import json
import sys
from flask import request
import mysql.connector
from datetime import datetime, timedelta

sys.path.append('/home/pengna/Workspace/General_info/scripts/Power/MonitorMultiPVs/')
from Monitor import Monitor

app = Flask(__name__)
socketio = SocketIO(app)

# 全局变量
output_pv_data = {}
print_lock = threading.Lock()

# EPICS 设置
epics.ca.initialize_libca()
context = epics.ca.current_context()

# Monitor 配置
config_path = '/home/control/Workspace/GeneralInfo/scripts/Power/MonitorMultiPVs/PS_config.json'
monitor_manager = Monitor(config_path, print_lock, context)

# 定义要监控的PV字典
pvs_to_monitor = {
    "LRBT_LRQPS02": "LRBT:LRQPS02::Alarm:Tmp",
    "RTBT_RTBVPS02": "RTBT:RTBVPS02::Alarm:Tmp",
    "MEBT_QPS09": "MEBT:QPS09::Alarm:Tmp",
    "DTL_QPS56": "DTL:QPS56::Alarm:Tmp",
    "DTL_QPS11": "DTL:QPS11::Alarm:Tmp",
    "RTBT_RDQPS05": "RTBT:RDQPS05::Alarm:Tmp",
    "DTL_QPS03": "DTL:QPS03::Alarm:Tmp",
    "RCS_R1DHPS07": "RCS:R1DHPS07::Alarm:Tmp",
    "DTL_QPS48": "DTL:QPS48::Alarm:Tmp",
    "RCS_R4DHPS07": "RCS:R4DHPS07::Alarm:Tmp",
    "DTL_QPS71": "DTL:QPS71::Alarm:Tmp",
    "MEBT_DHPS03": "MEBT:DHPS03::Alarm:Tmp",
    "RCS_R3DVPS08": "RCS:R3DVPS08::Alarm:Tmp",
    "DTL_QPS49": "DTL:QPS49::Alarm:Tmp",
    "RTBT_RTQPS27": "RTBT:RTQPS27::Alarm:Tmp",
    "RTBT_RTDVPS07": "RTBT:RTDVPS07::Alarm:Tmp",
    "DTL_QPS80": "DTL:QPS80::Alarm:Tmp",
    "LRBT_LRQPS03": "LRBT:LRQPS03::Alarm:Tmp",
    "LRBT_LRQPS01": "LRBT:LRQPS01::Alarm:Tmp",
    "DTL_QPS04": "DTL:QPS04::Alarm:Tmp",
    "MEBT_QPS08": "MEBT:QPS08::Alarm:Tmp",
    "LRBT_LDSWBPS01": "LRBT:LDSWBPS01::Alarm:Tmp",
    "DTL_QPS10": "DTL:QPS10::Alarm:Tmp",
    "DTL_QPS55": "DTL:QPS55::Alarm:Tmp",
    "LRBT_LRDHPS01": "LRBT:LRDHPS01::Alarm:Tmp",
    "DTL_QPS70": "DTL:QPS70::Alarm:Tmp",
    "MEBT_DHPS02": "MEBT:DHPS02::Alarm:Tmp",
    "RCS_R2DHPS02": "RCS:R2DHPS02::Alarm:Tmp",
    "DTL_QPS64": "DTL:QPS64::Alarm:Tmp",
    "LRBT_LRQPS10": "LRBT:LRQPS10::Alarm:Tmp",
    "RTBT_RTDVPS06": "RTBT:RTDVPS06::Alarm:Tmp",
    "RCS_R2DHPS04": "RCS:R2DHPS04::Alarm:Tmp",
    "DTL_QPS81": "DTL:QPS81::Alarm:Tmp",
    "RTBT_RTDVPS08": "RTBT:RTDVPS08::Alarm:Tmp",
    "DTL_QPS39": "DTL:QPS39::Alarm:Tmp",
    "LRBT_LRQPS04": "LRBT:LRQPS04::Alarm:Tmp",
    "MEBT_DHPS01": "MEBT:DHPS01::Alarm:Tmp",
    "RTBT_RTQPS09": "RTBT:RTQPS09::Alarm:Tmp",
    "RCS_R2DHPS12": "RCS:R2DHPS12::Alarm:Tmp",
    "RCS_SPS01": "RCS:SPS01::Alarm:Tmp",
    "LRBT_LRBPS01": "LRBT:LRBPS01::Alarm:Tmp",
    "DTL_QPS20": "DTL:QPS20::Alarm:Tmp",
    "RTBT_RDQPS03": "RTBT:RDQPS03::Alarm:Tmp",
    "LRBT_LRQPS11": "LRBT:LRQPS11::Alarm:Tmp",
    "LRBT_LRDHPS02": "LRBT:LRDHPS02::Alarm:Tmp",
    "DTL_QPS46": "DTL:QPS46::Alarm:Tmp",
    "RTBT_RTDVPS05": "RTBT:RTDVPS05::Alarm:Tmp",
    "RCS_R2DHPS01": "RCS:R2DHPS01::Alarm:Tmp",
    "DTL_QPS73": "DTL:QPS73::Alarm:Tmp",
    "DTL_QPS12": "DTL:QPS12::Alarm:Tmp",
    "LRBT_LRSWBPS01": "LRBT:LRSWBPS01::Alarm:Tmp",
    "DTL_QPS63": "DTL:QPS63::Alarm:Tmp",
    "RTBT_RDDHPS02": "RTBT:RDDHPS02::Alarm:Tmp",
    "RTBT_RTQPS29": "RTBT:RTQPS29::Alarm:Tmp",
    "RCS_R4DVPS11": "RCS:R4DVPS11::Alarm:Tmp",
    "RCS_R3DHPS09": "RCS:R3DHPS09::Alarm:Tmp",
    "DTL_QPS66": "DTL:QPS66::Alarm:Tmp",
    "RTBT_RTQPS26": "RTBT:RTQPS26::Alarm:Tmp",
    "MEBT_DHPS04": "MEBT:DHPS04::Alarm:Tmp",
    "DTL_QPS02": "DTL:QPS02::Alarm:Tmp",
    "RCS_R1DVPS11": "RCS:R1DVPS11::Alarm:Tmp",
    "DTL_QPS53": "DTL:QPS53::Alarm:Tmp",
    "MEBT_QPS06": "MEBT:QPS06::Alarm:Tmp",
    "DTL_QPS05": "DTL:QPS05::Alarm:Tmp",
    "LRBT_LRDVPS09": "LRBT:LRDVPS09::Alarm:Tmp",
    "MEBT_DVPS03": "MEBT:DVPS03::Alarm:Tmp",
    "LRBT_LRQPS21": "LRBT:LRQPS21::Alarm:Tmp",
    "DTL_QPS30": "DTL:QPS30::Alarm:Tmp",
    "DTL_QPS37": "DTL:QPS37::Alarm:Tmp",
    "LRBT_LRDVPS08": "LRBT:LRDVPS08::Alarm:Tmp",
    "LRBT_LRDHPS04": "LRBT:LRDHPS04::Alarm:Tmp",
    "MEBT_DHPS06": "MEBT:DHPS06::Alarm:Tmp",
    "RTBT_RTQPS23": "RTBT:RTQPS23::Alarm:Tmp",
    "LRBT_LRDVPS01": "LRBT:LRDVPS01::Alarm:Tmp",
    "RCS_SEPPS01": "RCS:SEPPS01::Alarm:Tmp",
    "MEBT_QPS05": "MEBT:QPS05::Alarm:Tmp",
    "RTBT_RTQPS08": "RTBT:RTQPS08::Alarm:Tmp",
    "RTBT_RTQPS01": "RTBT:RTQPS01::Alarm:Tmp",
    "DTL_QPS60": "DTL:QPS60::Alarm:Tmp",
    "LRBT_LRQPS14": "LRBT:LRQPS14::Alarm:Tmp",
    "DTL_QPS97": "DTL:QPS97::Alarm:Tmp",
    "DTL_QPS52": "DTL:QPS52::Alarm:Tmp",
    "DTL_QPS38": "DTL:QPS38::Alarm:Tmp",
    "LRBT_LRDHPS11": "LRBT:LRDHPS11::Alarm:Tmp",
    "RTBT_RTDVPS02": "RTBT:RTDVPS02::Alarm:Tmp",
    "DTL_QPS36": "DTL:QPS36::Alarm:Tmp",
    "RTBT_RTDHPS07": "RTBT:RTDHPS07::Alarm:Tmp",
    "LRBT_LRDVPS07": "LRBT:LRDVPS07::Alarm:Tmp",
    "RCS_R2DVPS02": "RCS:R2DVPS02::Alarm:Tmp",
    "DTL_QPS23": "DTL:QPS23::Alarm:Tmp",
    "RTBT_RTQPS30": "RTBT:RTQPS30::Alarm:Tmp",
    "RCS_HMBPS01": "RCS:HMBPS01::Alarm:Tmp",
    "DTL_QPS29": "DTL:QPS29::Alarm:Tmp",
    "LRBT_LRQPS07": "LRBT:LRQPS07::Alarm:Tmp",
    "LRBT_LRDVPS10": "LRBT:LRDVPS10::Alarm:Tmp",
    "DTL_QPS16": "DTL:QPS16::Alarm:Tmp",
    "DTL_QPS51": "DTL:QPS51::Alarm:Tmp",
    "MEBT_QPS04": "MEBT:QPS04::Alarm:Tmp",
    "RCS_HTBPS01": "RCS:HTBPS01::Alarm:Tmp",
    "DTL_QPS58": "DTL:QPS58::Alarm:Tmp",
    "DTL_QPS45": "DTL:QPS45::Alarm:Tmp",
    "LRBT_LRDHPS10": "LRBT:LRDHPS10::Alarm:Tmp",
    "RTBT_RTQPS02": "RTBT:RTQPS02::Alarm:Tmp",
    "RTBT_RDDHPS01": "RTBT:RDDHPS01::Alarm:Tmp",
    "DTL_QPS24": "DTL:QPS24::Alarm:Tmp",
    "RTBT_RTQPS28": "RTBT:RTQPS28::Alarm:Tmp",
    "DTL_QPS09": "DTL:QPS09::Alarm:Tmp",
    "RTBT_RTQPS14": "RTBT:RTQPS14::Alarm:Tmp",
    "MEBT_DHPS05": "MEBT:DHPS05::Alarm:Tmp",
    "DTL_QPS17": "DTL:QPS17::Alarm:Tmp",
    "DTL_QPS92": "DTL:QPS92::Alarm:Tmp",
    "LEBT_DVPS02": "LEBT:DVPS02::Alarm:Tmp",
    "DTL_QPS65": "DTL:QPS65::Alarm:Tmp",
    "LRBT_LRQPS08": "LRBT:LRQPS08::Alarm:Tmp",
    "RCS_R3DVPS11": "RCS:R3DVPS11::Alarm:Tmp",
    "LRBT_LRQPS22": "LRBT:LRQPS22::Alarm:Tmp",
    "RTBT_RTBPS02": "RTBT:RTBPS02::Alarm:Tmp",
    "RTBT_RTQPS22": "RTBT:RTQPS22::Alarm:Tmp",
    "DTL_QPS57": "DTL:QPS57::Alarm:Tmp",
    "LEBT_SOLPS03": "LEBT:SOLPS03::Alarm:Tmp",
    "DTL_QPS44": "DTL:QPS44::Alarm:Tmp",
    "DTL_QPS31": "DTL:QPS31::Alarm:Tmp",
    "LRBT_LRDVPS02": "LRBT:LRDVPS02::Alarm:Tmp",
    "RCS_R4DHPS01": "RCS:R4DHPS01::Alarm:Tmp",
    "RCS_R4DVPS05": "RCS:R4DVPS05::Alarm:Tmp",
    "MEBT_DVPS04": "MEBT:DVPS04::Alarm:Tmp",
    "RCS_R1DHPS01": "RCS:R1DHPS01::Alarm:Tmp",
    "RCS_R1DVPS05": "RCS:R1DVPS05::Alarm:Tmp",
    "LRBT_LRDHPS03": "LRBT:LRDHPS03::Alarm:Tmp",
    "DTL_QPS98": "DTL:QPS98::Alarm:Tmp",
    "RCS_BCPS01": "RCS:BCPS01::Alarm:Tmp",
    "LRBT_LRDHPS09": "LRBT:LRDHPS09::Alarm:Tmp",
    "DTL_QPS85": "DTL:QPS85::Alarm:Tmp",
    "RCS_R3DHPS12": "RCS:R3DHPS12::Alarm:Tmp",
    "RTBT_RTQPS07": "RTBT:RTQPS07::Alarm:Tmp",
    "RTBT_RDQPS04": "RTBT:RDQPS04::Alarm:Tmp",
    "RTBT_RTDHPS08": "RTBT:RTDHPS08::Alarm:Tmp",
    "DTL_QPS72": "DTL:QPS72::Alarm:Tmp",
    "RTBT_RTDVPS01": "RTBT:RTDVPS01::Alarm:Tmp",
    "RTBT_RTOCTVPS01": "RTBT:RTOCTVPS01::Alarm:Tmp",
    "LRBT_LRQPS15": "LRBT:LRQPS15::Alarm:Tmp",
    "DTL_QPS94": "DTL:QPS94::Alarm:Tmp",
    "RTBT_RTQPS04": "RTBT:RTQPS04::Alarm:Tmp",
    "LRBT_LRQPS09": "LRBT:LRQPS09::Alarm:Tmp",
    "DTL_QPS41": "DTL:QPS41::Alarm:Tmp",
    "MEBT_QPS02": "MEBT:QPS02::Alarm:Tmp",
    "LRBT_LRDHPS08": "LRBT:LRDHPS08::Alarm:Tmp",
    "LRBT_LRQPS17": "LRBT:LRQPS17::Alarm:Tmp",
    "RTBT_RTQPS12": "RTBT:RTQPS12::Alarm:Tmp",
    "DTL_QPS33": "DTL:QPS33::Alarm:Tmp",
    "RTBT_RTDHPS02": "RTBT:RTDHPS02::Alarm:Tmp",
    "DTL_QPS86": "DTL:QPS86::Alarm:Tmp",
    "LRBT_LRDVPS05": "LRBT:LRDVPS05::Alarm:Tmp",
    "LRBT_LRDHPS07": "LRBT:LRDHPS07::Alarm:Tmp",
    "DTL_QPS78": "DTL:QPS78::Alarm:Tmp",
    "MEBT_DVPS06": "MEBT:DVPS06::Alarm:Tmp",
    "DTL_QPS25": "DTL:QPS25::Alarm:Tmp",
    "LRBT_LRQPS16": "LRBT:LRQPS16::Alarm:Tmp",
    "DTL_QPS19": "DTL:QPS19::Alarm:Tmp",
    "MEBT_QPS01": "MEBT:QPS01::Alarm:Tmp",
    "DTL_QPS93": "DTL:QPS93::Alarm:Tmp",
    "DTL_QPS87": "DTL:QPS87::Alarm:Tmp",
    "RCS_R3DHPS04": "RCS:R3DHPS04::Alarm:Tmp",
    "DTL_QPS42": "DTL:QPS42::Alarm:Tmp",
    "MEBT_QPS10": "MEBT:QPS10::Alarm:Tmp",
    "LRBT_LRDVPS04": "LRBT:LRDVPS04::Alarm:Tmp",
    "RCS_R2DHPS09": "RCS:R2DHPS09::Alarm:Tmp",
    "RCS_AUXPS03": "RCS:AUXPS03::Alarm:Tmp",
    "RTBT_RTQPS11": "RTBT:RTQPS11::Alarm:Tmp",
    "DTL_QPS77": "DTL:QPS77::Alarm:Tmp",
    "DTL_QPS26": "DTL:QPS26::Alarm:Tmp",
    "RCS_R2DVPS05": "RCS:R2DVPS05::Alarm:Tmp",
    "RTBT_RTQPS05": "RTBT:RTQPS05::Alarm:Tmp",
    "DTL_QPS32": "DTL:QPS32::Alarm:Tmp",
    "LEBT_DVPS01": "LEBT:DVPS01::Alarm:Tmp",
    "RTBT_RTDHPS03": "RTBT:RTDHPS03::Alarm:Tmp",
    "DTL_QPS43": "DTL:QPS43::Alarm:Tmp",
    "LEBT_SOLPS02": "LEBT:SOLPS02::Alarm:Tmp",
    "RCS_R2DVPS08": "RCS:R2DVPS08::Alarm:Tmp",
    "RTBT_RTDHPS04": "RTBT:RTDHPS04::Alarm:Tmp",
    "RTBT_RTQPS21": "RTBT:RTQPS21::Alarm:Tmp",
    "DTL_QPS69": "DTL:QPS69::Alarm:Tmp",
    "LEBT_DHPS02": "LEBT:DHPS02::Alarm:Tmp",
    "RTBT_RTOCTHPS01": "RTBT:RTOCTHPS01::Alarm:Tmp",
    "MEBT_DVPS05": "MEBT:DVPS05::Alarm:Tmp",
    "RTBT_RDDVPS01": "RTBT:RDDVPS01::Alarm:Tmp",
    "LRBT_LRDVPS06": "LRBT:LRDVPS06::Alarm:Tmp",
    "RTBT_RTQPS10": "RTBT:RTQPS10::Alarm:Tmp",
    "DTL_QPS28": "DTL:QPS28::Alarm:Tmp",
    "DTL_QPS35": "DTL:QPS35::Alarm:Tmp",
    "DTL_QPS84": "DTL:QPS84::Alarm:Tmp",
    "LRBT_LRQPS19": "LRBT:LRQPS19::Alarm:Tmp",
    "LRBT_LRDVPS03": "LRBT:LRDVPS03::Alarm:Tmp",
    "RTBT_RTQPS06": "RTBT:RTQPS06::Alarm:Tmp",
    "DTL_QPS89": "DTL:QPS89::Alarm:Tmp",
    "DTL_QPS76": "DTL:QPS76::Alarm:Tmp",
    "DTL_QPS08": "DTL:QPS08::Alarm:Tmp",
    "DTL_QPS50": "DTL:QPS50::Alarm:Tmp",
    "MEBT_QPS03": "MEBT:QPS03::Alarm:Tmp",
    "RCS_AUXPS04": "RCS:AUXPS04::Alarm:Tmp",
    "RTBT_RTQPS03": "RTBT:RTQPS03::Alarm:Tmp",
    "DTL_QPS15": "DTL:QPS15::Alarm:Tmp",
    "RTBT_RTDHPS01": "RTBT:RTDHPS01::Alarm:Tmp",
    "RTBT_RTBPS01": "RTBT:RTBPS01::Alarm:Tmp",
    "RCS_R3DVPS02": "RCS:R3DVPS02::Alarm:Tmp",
    "RCS_R2DHPS07": "RCS:R2DHPS07::Alarm:Tmp",
    "DTL_QPS79": "DTL:QPS79::Alarm:Tmp",
    "LRBT_LRDHPS12": "LRBT:LRDHPS12::Alarm:Tmp",
    "DTL_QPS91": "DTL:QPS91::Alarm:Tmp",
    "DTL_QPS40": "DTL:QPS40::Alarm:Tmp",
    "RTBT_RTQPS13": "RTBT:RTQPS13::Alarm:Tmp",
    "DTL_QPS18": "DTL:QPS18::Alarm:Tmp",
    "RTBT_RTDVPS06A": "RTBT:RTDVPS06A::Alarm:Tmp",
    "DTL_QPS75": "DTL:QPS75::Alarm:Tmp",
    "RCS_R3DHPS01": "RCS:R3DHPS01::Alarm:Tmp",
    "DTL_QPS07": "DTL:QPS07::Alarm:Tmp",
    "RCS_R3DVPS05": "RCS:R3DVPS05::Alarm:Tmp",
    "DTL_QPS22": "DTL:QPS22::Alarm:Tmp",
    "RTBT_RTDVPS03": "RTBT:RTDVPS03::Alarm:Tmp",
    "LRBT_LRQPS13": "LRBT:LRQPS13::Alarm:Tmp",
    "RTBT_RTDHPS06": "RTBT:RTDHPS06::Alarm:Tmp",
    "DTL_QPS67": "DTL:QPS67::Alarm:Tmp",
    "RTBT_RTQPS31": "RTBT:RTQPS31::Alarm:Tmp",
    "LRBT_LRQPS06": "LRBT:LRQPS06::Alarm:Tmp",
    "DTL_QPS14": "DTL:QPS14::Alarm:Tmp",
    "RTBT_RDQPS01": "RTBT:RDQPS01::Alarm:Tmp",
    "DTL_QPS90": "DTL:QPS90::Alarm:Tmp",
    "DTL_QPS59": "DTL:QPS59::Alarm:Tmp",
    "RCS_R1DHPS04": "RCS:R1DHPS04::Alarm:Tmp",
    "RCS_R4DHPS04": "RCS:R4DHPS04::Alarm:Tmp",
    "LRBT_LRDHPS05": "LRBT:LRDHPS05::Alarm:Tmp",
    "LRBT_LRDVPS00": "LRBT:LRDVPS00::Alarm:Tmp",
    "DTL_QPS06": "DTL:QPS06::Alarm:Tmp",
    "LRBT_LRQPS20": "LRBT:LRQPS20::Alarm:Tmp",
    "DTL_QPS61": "DTL:QPS61::Alarm:Tmp",
    "RCS_R1DHPS12": "RCS:R1DHPS12::Alarm:Tmp",
    "RCS_R4DHPS12": "RCS:R4DHPS12::Alarm:Tmp",
    "MEBT_DVPS02": "MEBT:DVPS02::Alarm:Tmp",
    "RCS_R3LMTDHPS01": "RCS:R3LMTDHPS01::Alarm:Tmp",
    "RTBT_RTQPS24": "RTBT:RTQPS24::Alarm:Tmp",
    "DTL_QPS68": "DTL:QPS68::Alarm:Tmp",
    "RCS_R2DVPS11": "RCS:R2DVPS11::Alarm:Tmp",
    "DTL_QPS74": "DTL:QPS74::Alarm:Tmp",
    "LEBT_DHPS01": "LEBT:DHPS01::Alarm:Tmp",
    "RTBT_RTDVPS09": "RTBT:RTDVPS09::Alarm:Tmp",
    "RTBT_RDQPS02": "RTBT:RDQPS02::Alarm:Tmp",
    "RCS_LAMPS01": "RCS:LAMPS01::Alarm:Tmp",
    "RCS_SEPPS02": "RCS:SEPPS02::Alarm:Tmp",
    "DTL_QPS83": "DTL:QPS83::Alarm:Tmp",
    "DTL_QPS13": "DTL:QPS13::Alarm:Tmp",
    "DTL_QPS96": "DTL:QPS96::Alarm:Tmp",
    "LEBT_SOLPS01": "LEBT:SOLPS01::Alarm:Tmp",
    "DTL_QPS88": "DTL:QPS88::Alarm:Tmp",
    "RCS_R4DHPS09": "RCS:R4DHPS09::Alarm:Tmp",
    "MEBT_QPS07": "MEBT:QPS07::Alarm:Tmp",
    "DTL_QPS54": "DTL:QPS54::Alarm:Tmp",
    "DTL_QPS62": "DTL:QPS62::Alarm:Tmp",
    "RCS_AUXPS02": "RCS:AUXPS02::Alarm:Tmp",
    "RCS_R3DHPS07": "RCS:R3DHPS07::Alarm:Tmp",
    "RCS_R3LMTDVPS01": "RCS:R3LMTDVPS01::Alarm:Tmp",
    "DTL_QPS01": "DTL:QPS01::Alarm:Tmp",
    "RCS_R1DHPS09": "RCS:R1DHPS09::Alarm:Tmp",
    "RCS_R4DVPS02": "RCS:R4DVPS02::Alarm:Tmp",
    "RTBT_RTQPS25": "RTBT:RTQPS25::Alarm:Tmp",
    "RCS_R1DVPS02": "RCS:R1DVPS02::Alarm:Tmp",
    "RTBT_RTBVPS01": "RTBT:RTBVPS01::Alarm:Tmp",
    "MEBT_DVPS01": "MEBT:DVPS01::Alarm:Tmp",
    "RTBT_RTDHPS05": "RTBT:RTDHPS05::Alarm:Tmp",
    "RCS_SPS02": "RCS:SPS02::Alarm:Tmp",
    "DTL_QPS27": "DTL:QPS27::Alarm:Tmp",
    "LRBT_LRQPS18": "LRBT:LRQPS18::Alarm:Tmp",
    "DTL_QPS82": "DTL:QPS82::Alarm:Tmp",
    "DTL_QPS95": "DTL:QPS95::Alarm:Tmp",
    "LRBT_LRQPS12": "LRBT:LRQPS12::Alarm:Tmp",
    "LRBT_LRQPS05": "LRBT:LRQPS05::Alarm:Tmp",
    "DTL_QPS34": "DTL:QPS34::Alarm:Tmp",
    "RCS_R4DVPS08": "RCS:R4DVPS08::Alarm:Tmp",
    "RTBT_RTDVPS04": "RTBT:RTDVPS04::Alarm:Tmp",
    "DTL_QPS47": "DTL:QPS47::Alarm:Tmp",
    "DTL_QPS21": "DTL:QPS21::Alarm:Tmp",
    "RCS_R1DVPS08": "RCS:R1DVPS08::Alarm:Tmp",
    "LRBT_LDDVPS01": "LRBT:LDDVPS01::Alarm:Tmp",
    "RTBT_RDDVPS02": "RTBT:RDDVPS02::Alarm:Tmp",
    "RTBT_RTQPS32": "RTBT:RTQPS32::Alarm:Tmp",
    "LRBT_LRDHPS06": "LRBT:LRDHPS06::Alarm:Tmp"
}

# 更新频率设置
UPDATE_FREQUENCY = 1  # 每秒更新一次

def monitor_pv(variable_name, pv_name):
    epics.ca.attach_context(context)
    while True:
        try:
            value = epics.caget(pv_name)
            with print_lock:
                output_pv_data[variable_name] = value
            socketio.emit('update_data', {'variable_name': variable_name, 'value': value})
        except Exception as e:
            print(f"Error reading PV {pv_name}: {e}")
        time.sleep(UPDATE_FREQUENCY)

def start_monitoring():
    for variable_name, pv_name in pvs_to_monitor.items():
        thread = threading.Thread(target=monitor_pv, args=(variable_name, pv_name))
        thread.daemon = True  # 设置为守护线程
        thread.start()
        
def fetch_historical_data_from_mysql(pv_name, start_date, end_date):
    """
    从 MySQL 数据库查询指定 PV 的历史报警时间
    """
    try:
        connection = mysql.connector.connect(
            host='10.1.44.223',
            port=3306,
            database='archive',
            user='archive',
            password='123456'
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            historical_data = []

            # 查询 channel_id 对应的 pv_name
            cursor.execute(f"SELECT channel_id FROM channel WHERE name = '{pv_name}'")
            channel_result = cursor.fetchone()

            if channel_result:
                channel_id = channel_result['channel_id']

                # 查询历史数据
                query = f"""
                SELECT smpl_time, float_val
                FROM sample
                WHERE channel_id = {channel_id}
                    AND smpl_time BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY smpl_time DESC;
                """
                cursor.execute(query)
                results = cursor.fetchall()

                # 找到最近的报警时间
                last_alarm_time = next((row['smpl_time'] for row in results if row['float_val'] == 1), None)

                return {
                    'pv_name': pv_name,
                    'last_alarm_time': last_alarm_time.strftime('%Y-%m-%d %H:%M:%S') if last_alarm_time else "无"
                }

    except mysql.connector.Error as e:
        print(f"MySQL Error: {e}")
        return {'pv_name': pv_name, 'last_alarm_time': "无"}

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/api/fetch-historical-data', methods=['POST'])
def fetch_historical_data():
    """
    提供所有 PV 名称的历史报警时间接口
    """
    data = request.json
    start_date = data.get('start_date', (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'))
    end_date = data.get('end_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # 查询所有 pvs_to_monitor 的历史报警时间
    historical_data = []
    for variable_name, pv_name in pvs_to_monitor.items():
        pv_data = fetch_historical_data_from_mysql(pv_name, start_date, end_date)
        # 添加变量名 (key) 到返回结果中
        pv_data['variable_name'] = variable_name
        historical_data.append(pv_data)

    return jsonify(historical_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    with print_lock:
        data = output_pv_data.copy()
    return jsonify(data)

@socketio.on('connect')
def handle_connect():
    with print_lock:
        for variable_name, value in output_pv_data.items():
            emit('update_data', {'variable_name': variable_name, 'value': value})

if __name__ == '__main__':
    start_monitoring()
    socketio.run(app, host='0.0.0.0', port=5008)