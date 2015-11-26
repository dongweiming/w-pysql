# 说明 #

直接运行python wsql.py文件或rlwrap python wsql.py


# 设置与使用 #

  * 命令q退出程序。
  * mode mode\_name命令可在不同模式下切换，参数mode\_name可设为sql、py、或kdb。
  * use db\_name命令可在不同服务器不同数据库之间切换，具体可看sqlstore.py的配置。默认可使用luz, orc, ent, elf, rohan等参数，扩展参数可参考sqlstore.py。
  * host host\_name命令可指定KDB查询主机，host\_name可设定为boromir或gimli。
  * limit num命令可以设定显示的结果行数，默认为只显示100行。
  * 可以在py模式下拼接好语句之后赋给一个变量，再切换sql或kdb模式下输入该变量即可运行相应命令。如：
```
sql>mode py 
py>uid=2101576
py>ss='select * from user where uid=%s'%uid
py>mode sql
sql>ss
...
```