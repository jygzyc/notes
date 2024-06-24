---
title: Android逆向中的字符串加密和反混淆
slug: technology/android/reverse/discussion-12/
number: 12
url: https://github.com/jygzyc/notes/discussions/12
created: 2024-05-27
updated: 2024-06-24
authors: [jygzyc]
categories: 
  - 0101-Android
labels: ['010103-逆向分析']
comments: true
---

<!-- string_decryption_in_android_reverse_engineering -->

## 字符串加密概述

目前，主流的App上都有了字符串的加密和混淆，这对于逆向和安全检测来说，无疑是加大了难度；同时，对于恶意应用来说，也方便了他们隐藏真实的意图。针对这种情况，写了一个小工具抛砖引玉解决这类问题

<!-- more -->

以某网站上的著名项目`StringFog`为例，这是一款自动对dex/aar/jar文件中的字符串进行加密Android插件工具，其工作如下所示

![string_decryption_in_android_reverse_engineering_01.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_01.png)

`StringFog`实现的原理实际上非常简单，就是在字节码层面进行替换，但是却能给逆向分析增加较大的时间成本，并且，除了`StringFog`，市面上也存在很多自定义加密字符串的方案，这类方案往往和混淆结合在一起，就如同逆向时的鸡肋一般，让安全研究人员食之无味，弃之可惜。

## 案例一：某dex

通过`jadx`加载某dex文件时，会发现文件中存在很多的加密字符串，这样的加密很影响分析的效率，那么我们怎么去除它呢？在最新版本的`jadx`中，开发者引入了一个全新的功能——`jadx-script`。通过`jadx-script`，我们能够在`jadx`中执行kotlin script，而相关的例子，也放在`jadx-plugins/jadx-script/examples/scripts`中，下面会介绍到。

![string_decryption_in_android_reverse_engineering_02.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_02.png)

跟踪这个解密的函数，能看到解密的逻辑并不复杂，完全能够直接复现，那么我们期望的效果，肯定是在静态分析时直接看到解密后的结果，下面我们就来看看怎么达到这个效果。事实上，我们可以编写一个算法还原的脚本并交给最新的`jadx`去执行

![string_decryption_in_android_reverse_engineering_03.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_03.png)

```kotlin
/**
 * Replace method call with calculated result.
 * Useful for custom string deobfuscation.
 *
 * Example for sample from issue https://github.com/skylot/jadx/issues/1251
 */

import jadx.core.dex.instructions.ConstStringNode
import jadx.core.dex.instructions.InvokeNode
import jadx.core.dex.instructions.args.InsnArg
import jadx.core.dex.instructions.args.InsnWrapArg
import jadx.core.dex.instructions.args.RegisterArg


val jadx = getJadxInstance()

val mthSignature = "com.xshield.aa.iIiIiiiiII(Ljava/lang/String;)Ljava/lang/String;"

jadx.replace.insns { mth, insn ->
	if (insn is InvokeNode && insn.callMth.rawFullId == mthSignature) {
		val str = getConstStr(insn.getArg(0))
		if (str != null) {
			val resultStr = decode(str)
			log.info { "Decode '$str' to '$resultStr' in $mth" }
			return@insns ConstStringNode(resultStr)
		}
	}
	null
}

fun getConstStr(arg: InsnArg): String? {
	val insn = when (arg) {
		is InsnWrapArg -> arg.wrapInsn
		is RegisterArg -> arg.assignInsn
		else -> null
	}
	if (insn is ConstStringNode) {
		return insn.string
	}
	return null
}

/**
 * Decompiled method, automatically converted to Kotlin by IntelliJ Idea
 */
fun decode(str: String): String {
	val length = str.length
	val cArr = CharArray(length)
	var i = length - 1
	while (i >= 0) {
		val i2 = i - 1
		cArr[i] = (str[i].code xor 'z'.code).toChar()
		if (i2 < 0) {
			break
		}
		i = i2 - 1
		cArr[i2] = (str[i2].code xor '\u000c'.code).toChar()
	}
	return String(cArr)
}
```

上面的代码中，已经复现了解密的算法，接下来就是加载脚本了，在GUI中选择`replace_method_call.jadx.kts`，打开

![string_decryption_in_android_reverse_engineering_04.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_04.png)

执行脚本，会遍历每一个方法节点，当签名相符时，会替换为解密后的结果

![string_decryption_in_android_reverse_engineering_05.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_05.png)

这样的话，我们就可以继续正常逆向分析了

## 案例二：某Demo APK

通过上面的案例，我们发现可以通过逆向的手段还原算法，但是如果碰到不能够还原的加密方法，是不是就无法解密了呢？其实不然，因为我们还有`Frida`或者`unidbg`，这两者在函数的主动调用上都是一把好手，具体的对比如下表所示

|        | Java层函数调用 | Native层函数调用 | 稳定性 |
| ------ | -------------- | ---------------- | ------ |
| Frida  | 可以           | 可以             | 不稳定 |
| unidbg | 不可以         | 可以             | 稳定   |

我们可以根据各自的特性选择主动调用的工具，这里先看一个`Demo`案例，以`androidx.core.utils.CommenUtils$Companion.a`函数为例

![string_decryption_in_android_reverse_engineering_06.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_06.png)

通过上图，我们能明显看到关键字符串均采用了加密，那么看一下加密函数`C3632qz.b`的实现

![string_decryption_in_android_reverse_engineering_07.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_07.png)

发现这里实际上是Base64的解密，当然，我们可以在脚本中实现Base64的解密算法，不过这里也可以采用另一种方式解决，那就是直接hook `C3632qz.b`函数，进而主动调用返回结果，具体怎么操作呢？上代码

```kotlin
// That is the path relative to the jadx/bin execution directory, or it can be changed to an absolute path.
@file:DependsOn("../external_library/okhttp-4.11.0.jar")
@file:DependsOn("../external_library/okio-jvm-3.2.0.jar")
@file:DependsOn("../external_library/okio-3.2.0.jar")

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response

import jadx.core.dex.instructions.ConstStringNode
import jadx.core.dex.instructions.InvokeNode
import jadx.core.dex.instructions.args.InsnArg
import jadx.core.dex.instructions.args.InsnWrapArg
import jadx.core.dex.instructions.args.RegisterArg

val jadx = getJadxInstance()

val mthSignature_qzb = "kotlinx.android.extensionss.qz.b(Ljava/lang/String;)Ljava/lang/String;"

jadx.replace.insns { mth, insn ->
	if (insn is InvokeNode && insn.callMth.rawFullId == mthSignature_qzb) {
		val str = getConstStr(insn.getArg(0))
		if (str != null) {
			val resultStr = decrypt(mthSignature_qzb, str)
			log.info { "Decrypt '$str' to '$resultStr' in $mth" }
			return@insns ConstStringNode(resultStr)
		}
	}
	null
}
fun getConstStr(arg: InsnArg): String? {
	val insn = when (arg) {
		is InsnWrapArg -> arg.wrapInsn
		is RegisterArg -> arg.assignInsn
		else -> null
	}
	if (insn is ConstStringNode) {
		return insn.string
	}
	return null
}
// rpc 解密函数
fun decrypt(mthSignature: String, param: String): String?{
	val client = OkHttpClient()
    val json = """
        {
            "method": "${mthSignature}",
			"param": "${param}"
        }
    """.trimIndent()

	val requestBody = json.toRequestBody("application/json; charset=utf-8".toMediaType())

	val request = Request.Builder()
        .url("http://127.0.0.1:5000/decrypt")
        .post(requestBody)
        .build()

    val response = client.newCall(request).execute()
	return response.body?.string().toString()
}
```

能够发现，其实脚本的主体结构并没有太大的变化，但是在核心的`decrypt`函数上，使用了`OkHttp`发送请求，并接受返回的数据，即是将`jadx`作为了客户端。既然有客户端，那么也得有服务端，如下所示

```python
# ...
app = Flask(__name__)
logger = Logger(log_level="INFO")

def message(message, data):
    if message['type'] == 'send':
        logger.debug(f"[*] {message['payload']}")
    else:
        logger.debug(message)

@app.route('/decrypt', methods=['POST'])#data解密
def decrypt_class():
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    logger.info(json_data)
    method_sig = json_data.get("method")
    method_param = handle_params(json_data.get("param"))
    logger.debug(f"method: ${method_sig}; params: ${method_param}") 
    handle_method = globals()[methods[method_sig]]
    res = _process_string(handle_method(method_sig, method_param))
    response = make_response(res, 200)
    response.headers['Content-Type'] = 'application/json'
    return response

def _process_string(s: str) -> str:
    s = ' '.join(s.split())
    s = re.sub(r'\s+', ' ', s)
    if len(s) > 0 and s[0] == ' ':
        s = ' ' + s.lstrip()
    if len(s) > 0 and s[-1] == ' ':
        s = s.rstrip() + ' '
    return s

def handle_params(params):
    return params

#################### Method Handler ####################

def _handle_qz_b(method_name, method_param):
    res = _process_string(script.exports_sync.invokemethod01(method_param))
    logger.info(f"{method_param} => {res}")
    return res

def _handle_cg_b(method_name, method_param):
    res = _process_string(script.exports_sync.invokemethod02(method_param))
    logger.info(f"{method_param} => {res}")
    return res

#################### Flask Server ####################

config = Config.builder()
methods = config.methods_map

device = frida.get_device_manager().add_remote_device(config.remote_device)
if(config.spawn):
    session = device.spawn(config.package_name)
else:
    session = device.attach(config.app_name)

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", config.frida_script_name)) as f:
    jsCode = f.read()

script = session.create_script(jsCode)
script.on("message",message)
script.load()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
```

由于我们的目标是如何完成RPC函数，故不会对上面的代码进行更深入的说明，但是有几个点需要注意，这也是本人踩过的坑

- 服务端处理完字符串数据后，一定要对字符串内的空格和回车做处理，否则会导致替换回去的数据出现显示问题
- 在`Frida` 15及以上的版本，attach操作需要应用的名称，由于笔者本人使用的是**Frida 16.0.19**，所以在这里也做了特殊的处理
- 我们可以在`Config`中提前设置好方法签名和函数的对应，例如`"kotlinx.android.extensionss.qz.b(Ljava/lang/String;)Ljava/lang/String;": "_handle_qz_b"`，这样就能根据不同的签名走不同的主动调用

开启Frida，启动PC端server，执行脚本，能够看到大部分内容已经被解密了

![string_decryption_in_android_reverse_engineering_08.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_08.png)

但是此时还需要注意一下`CornerTreatment.b("237A88EB")`，这看上去也是一个解密，跟进去看看

![string_decryption_in_android_reverse_engineering_09.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_09.png)

果不其然，这里也是一层加密，事实上，这个Demo中也存在着很多这种嵌套解密

![string_decryption_in_android_reverse_engineering_10.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_10.png)

虽然多了一层解密，但是我们依然可以如法炮制，再上一个解密的插件，这样问题就解决了，双层嵌套解密也能被干掉

![string_decryption_in_android_reverse_engineering_11.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_11.png)

![string_decryption_in_android_reverse_engineering_12.png](https://bucket.lilac.fun/2024/06/string_decryption_in_android_reverse_engineering_12.png)

当字符串的混淆消失之后，我们也能够更好地分析应用的行为，也可以将patch后的项目导出用于静态检测。

## 总结

上面的案例中我们只使用了Frida进行了字符串的还原，实际上，也存在App将字符串解密的函数放在Native中，这时候就需要更加稳定的unidbg去解了，笔者在这里只是引出一个思路，关于unidbg的使用就不再赘述了。总而言之，只要能通过这种`jadx`脚本的方式继续patch，那么字符串加密的问题就不再会成为逆向分析的时间成本，笔者也将相关的代码和最新版编译的`jadx`一并放出，可供参考。

[jygzyc/apkDeobfuscation (github.com)](https://github.com/jygzyc/apkDeobfuscation)

## 参考资料

- [MegatronKing/StringFog: 一款自动对字节码中的字符串进行加密Android插件工具 (github.com)](https://github.com/MegatronKing/StringFog)
- [frida/frida: Clone this repo to build Frida (github.com)](https://github.com/frida/frida)
- [skylot/jadx: Dex to Java decompiler (github.com)](https://github.com/skylot/jadx)