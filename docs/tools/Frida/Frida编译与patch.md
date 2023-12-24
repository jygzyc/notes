# Frida编译与patch

## Frida编译

### 代码同步与环境准备

> Windows 11 + vmware Ubuntu 22.04 虚拟机，在虚拟机中进行了操作

使用`git clone --recurse-submodules https://github.com/frida/frida.git`即可同步Frida的全部代码，如果要使用特定tag的代码可以使用如下的命令创建新的分支，这里以笔者最新的**16.0.19**版本为例

```bash
$ git checkout -b branch-16.0.19 16.0.19
Switched to a new branch 'branch-16.0.19'
```

这样的话就切换到了创建的分支，并可以基于该分支修改文件了，这里我新建一个基于main的分支并进行修改

想要编译Frida，首先要配置好对应的NDK版本，我们在`frida/releng/setup-env.sh`下能够找到`ndk_required`，这里说明了所需的NDK版本

```sh
...
if [ "$host_os" == "android" ]; then
  ndk_required=25
  if [ -n "$ANDROID_NDK_ROOT" ] && [ -e "$ANDROID_NDK_ROOT" ]; then
    if [ -f "$ANDROID_NDK_ROOT/source.properties" ]; then
      ndk_installed_version=$(grep Pkg.Revision "$ANDROID_NDK_ROOT/source.properties" | awk '{ split($NF, v, "."); print v[1]; }')
    else
      ndk_installed_version=$(cut -f1 -d" " "$ANDROID_NDK_ROOT/RELEASE.TXT")
...
```

以文章编写时的最新版本为例，这里能看到需要的Android NDK version 是25，下载NDK并安装

```bash
wget https://dl.google.com/android/repository/android-ndk-r25c-linux.zip
unzip android-ndk-r25c-linux.zip
echo 'export ANDROID_NDK_ROOT=/home/ecool/Tools/android-ndk-r25c' >> ~/.zshrc
echo 'export PATH=$ANDROID_NDK_ROOT:$PATH' >> ~/.zshrc
source ~/.zshrc
```

除此以外，还需要安装Python和Nodejs，执行官网的命令即可

```bash
sudo apt-get install build-essential curl git lib32stdc++-9-dev \
    libc6-dev-i386 nodejs npm python3-dev python3-pip
```

### 编译

进入`frida`主目录后执行`make core-android-arm64`即可进行编译，在这期间需要科学上网，编译过程中会下载所需的SDK文件，一切顺利的话，会显示`Compilation succeeded`

```bash
[23/102] Compiling Vala source src/frida-data-android.vapi src/frida-data-helper-process.vapi src/fri...ler/compiler.vala src/frida-helper-backend.vapi lib/base/frida-base-1.0.vapi lib/pipe/frida-pipe.vapi
glib-2.0.vapi:1638.1-1638.14: warning: Namespace `GLib' does not have a GIR namespace and version annotation
 1638 | namespace GLib {
      | ^~~~~~~~~~~~~~
Compilation succeeded - 1 warning(s)
[102/102] Linking target tests/frida-tests
Installing lib/base/libfrida-base-1.0.a to /home/ecool/SourceCode/frida/build/frida-android-arm64/lib
Installing lib/base/frida-base.h to /home/ecool/SourceCode/frida/build/frida-android-arm64/include/frida-1.0
Installing lib/base/frida-base-1.0.vapi to /home/ecool/SourceCode/frida/build/frida-android-arm64/share/vala/vapi
Installing lib/payload/libfrida-payload-1.0.a to /home/ecool/SourceCode/frida/build/frida-android-arm64/lib
Installing lib/payload/frida-payload.h to /home/ecool/SourceCode/frida/build/frida-android-arm64/include/frida-1.0
Installing lib/payload/frida-payload-1.0.vapi to /home/ecool/SourceCode/frida/build/frida-android-arm64/share/vala/vapi
Installing lib/gadget/frida-gadget.so to /home/ecool/SourceCode/frida/build/frida-android-arm64/lib/frida/64
Installing src/api/frida-core.h to /home/ecool/SourceCode/frida/build/frida-android-arm64/include/frida-1.0
Installing src/api/frida-core-1.0.vapi to /home/ecool/SourceCode/frida/build/frida-android-arm64/share/vala/vapi
Installing src/api/frida-core-1.0.deps to /home/ecool/SourceCode/frida/build/frida-android-arm64/share/vala/vapi
Installing src/api/libfrida-core-1.0.a to /home/ecool/SourceCode/frida/build/frida-android-arm64/lib
Installing server/frida-server to /home/ecool/SourceCode/frida/build/frida-android-arm64/bin
Installing portal/frida-portal to /home/ecool/SourceCode/frida/build/frida-android-arm64/bin
Installing inject/frida-inject to /home/ecool/SourceCode/frida/build/frida-android-arm64/bin
Installing /home/ecool/SourceCode/frida/frida-core/lib/selinux/frida-selinux.h to /home/ecool/SourceCode/frida/build/frida-android-arm64/include/frida-1.0/
Installing /home/ecool/SourceCode/frida/build/tmp-android-arm64/frida-core/meson-private/frida-base-1.0.pc to /home/ecool/SourceCode/frida/build/frida-android-arm64/lib/pkgconfig
Installing /home/ecool/SourceCode/frida/build/tmp-android-arm64/frida-core/meson-private/frida-payload-1.0.pc to /home/ecool/SourceCode/frida/build/frida-android-arm64/lib/pkgconfig
Installing /home/ecool/SourceCode/frida/build/tmp-android-arm64/frida-core/meson-private/frida-core-1.0.pc to /home/ecool/SourceCode/frida/build/frida-android-arm64/lib/pkgconfig
make[1]: Leaving directory '/home/ecool/SourceCode/frida'
```

在`frida/build/frida-android-arm64/bin`文件夹下会有生成的`frida-server`文件

## Frida Patch

> 这里主要参考的是hluwa大佬对Frida的patches，且依照 [.kk](https://bbs.kanxue.com/user-home-918604.htm)大佬的文章做了部分的修改

### 16.0.19版本

这里没有修改运行默认目录（`/data/local/tmp`），也没有修改默认端口（27042），如果有需要可以自行修改。

#### 0001-ecool_string_frida_rpc.patch

```bash
From ea51ce9bccec1391f0050dcf6aa1e075a93b1cbd Mon Sep 17 00:00:00 2001
From: ecool <ecool@example.com>
Date: Fri, 9 Jun 2023 00:04:24 +0800
Subject: [PATCH] 0001_ecool_string_frida_rpc

---
 lib/base/rpc.vala | 6 +++---
 1 file changed, 3 insertions(+), 3 deletions(-)

diff --git a/lib/base/rpc.vala b/lib/base/rpc.vala
index 3695ba8c..02602abf 100644
--- a/lib/base/rpc.vala
+++ b/lib/base/rpc.vala
@@ -17,7 +17,7 @@ namespace Frida {
 			var request = new Json.Builder ();
 			request
 				.begin_array ()
-				.add_string_value ("frida:rpc")
+				.add_string_value ((string) GLib.Base64.decode("ZnJpZGE6cnBj="))
 				.add_string_value (request_id)
 				.add_string_value ("call")
 				.add_string_value (method)
@@ -70,7 +70,7 @@ namespace Frida {
 		}
 
 		public bool try_handle_message (string json) {
-			if (json.index_of ("\"frida:rpc\"") == -1)
+			if (json.index_of ((string) GLib.Base64.decode("ImZyaWRhOnJwYyI=")) == -1)
 				return false;
 
 			var parser = new Json.Parser ();
@@ -99,7 +99,7 @@ namespace Frida {
 				return false;
 
 			string? type = rpc_message.get_element (0).get_string ();
-			if (type == null || type != "frida:rpc")
+			if (type == null || type != (string) GLib.Base64.decode("ZnJpZGE6cnBj="))
 				return false;
 
 			var request_id_value = rpc_message.get_element (1);
-- 
2.34.1
```

#### 0002-ecool_io_re_frida_server.patch

```bash
From 398c83b1ac39586687355238a850ffa6fd194b46 Mon Sep 17 00:00:00 2001
From: ecool <ecool@example.com>
Date: Fri, 9 Jun 2023 00:18:50 +0800
Subject: [PATCH] ecool_io_re_frida_server

---
 server/server.vala | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

diff --git a/server/server.vala b/server/server.vala
index b758be07..44fb51fc 100644
--- a/server/server.vala
+++ b/server/server.vala
@@ -1,7 +1,7 @@
 namespace Frida.Server {
 	private static Application application;
 
-	private const string DEFAULT_DIRECTORY = "re.frida.server";
+	private const string DEFAULT_DIRECTORY = "re.ecool.server";
 	private static bool output_version = false;
 	private static string? listen_address = null;
 	private static string? certpath = null;
-- 
2.34.1
```

#### 0003-ecool_io_frida_agent_so.patch

```bash
From 0e21fac70c897fc3d9d7d7fc05a6394f0e28697a Mon Sep 17 00:00:00 2001
From: ecool <ecool@example.com>
Date: Fri, 9 Jun 2023 00:26:12 +0800
Subject: [PATCH] ecool_io_frida_agent_so

---
 src/linux/linux-host-session.vala | 7 ++++---
 1 file changed, 4 insertions(+), 3 deletions(-)

diff --git a/src/linux/linux-host-session.vala b/src/linux/linux-host-session.vala
index 50470ac8..87d41dba 100644
--- a/src/linux/linux-host-session.vala
+++ b/src/linux/linux-host-session.vala
@@ -128,12 +128,13 @@ namespace Frida {
 			var blob64 = Frida.Data.Agent.get_frida_agent_64_so_blob ();
 			var emulated_arm = Frida.Data.Agent.get_frida_agent_arm_so_blob ();
 			var emulated_arm64 = Frida.Data.Agent.get_frida_agent_arm64_so_blob ();
-			agent = new AgentDescriptor (PathTemplate ("frida-agent-<arch>.so"),
+			var random_prefix = "ecool" + GLib.Uuid.string_random();
+			agent = new AgentDescriptor (PathTemplate (random_prefix + "-<arch>.so"),
 				new Bytes.static (blob32.data),
 				new Bytes.static (blob64.data),
 				new AgentResource[] {
-					new AgentResource ("frida-agent-arm.so", new Bytes.static (emulated_arm.data), tempdir),
-					new AgentResource ("frida-agent-arm64.so", new Bytes.static (emulated_arm64.data), tempdir),
+					new AgentResource (random_prefix + "-arm.so", new Bytes.static (emulated_arm.data), tempdir),
+					new AgentResource (random_prefix + "-arm64.so", new Bytes.static (emulated_arm64.data), tempdir),
 				},
 				AgentMode.INSTANCED,
 				tempdir);
-- 
2.34.1
```

#### 0004-ecool_frida_agent_main.patch

```bash
From ec2c51fbf123462bc5cf194aa5e9304e5059f622 Mon Sep 17 00:00:00 2001
From: ecool <ecool@example.com>
Date: Fri, 9 Jun 2023 00:33:09 +0800
Subject: [PATCH] ecool_frida_agent_main

---
 src/agent-container.vala              | 2 +-
 src/darwin/darwin-host-session.vala   | 2 +-
 src/freebsd/freebsd-host-session.vala | 2 +-
 src/linux/linux-host-session.vala     | 2 +-
 src/qnx/qnx-host-session.vala         | 2 +-
 src/windows/windows-host-session.vala | 2 +-
 6 files changed, 6 insertions(+), 6 deletions(-)

diff --git a/src/agent-container.vala b/src/agent-container.vala
index a8db6b29..ae9c3451 100644
--- a/src/agent-container.vala
+++ b/src/agent-container.vala
@@ -25,7 +25,7 @@ namespace Frida {
 			assert (container.module != null);
 
 			void * main_func_symbol;
-			var main_func_found = container.module.symbol ("frida_agent_main", out main_func_symbol);
+			var main_func_found = container.module.symbol ("ecool_main", out main_func_symbol);
 			assert (main_func_found);
 			container.main_impl = (AgentMainFunc) main_func_symbol;
 
diff --git a/src/darwin/darwin-host-session.vala b/src/darwin/darwin-host-session.vala
index 2e9c010b..8e4f2235 100644
--- a/src/darwin/darwin-host-session.vala
+++ b/src/darwin/darwin-host-session.vala
@@ -354,7 +354,7 @@ namespace Frida {
 		private async uint inject_agent (uint pid, string agent_parameters, Cancellable? cancellable) throws Error, IOError {
 			uint id;
 
-			unowned string entrypoint = "frida_agent_main";
+			unowned string entrypoint = "ecool_main";
 #if HAVE_EMBEDDED_ASSETS
 			id = yield fruitjector.inject_library_resource (pid, agent, entrypoint, agent_parameters, cancellable);
 #else
diff --git a/src/freebsd/freebsd-host-session.vala b/src/freebsd/freebsd-host-session.vala
index a2204a4e..459f7697 100644
--- a/src/freebsd/freebsd-host-session.vala
+++ b/src/freebsd/freebsd-host-session.vala
@@ -197,7 +197,7 @@ namespace Frida {
 
 			var stream_request = Pipe.open (t.local_address, cancellable);
 
-			var id = yield binjector.inject_library_resource (pid, agent_desc, "frida_agent_main",
+			var id = yield binjector.inject_library_resource (pid, agent_desc, "ecool_main",
 				make_agent_parameters (pid, t.remote_address, options), cancellable);
 			injectee_by_pid[pid] = id;
 
diff --git a/src/linux/linux-host-session.vala b/src/linux/linux-host-session.vala
index 87d41dba..d8442fdb 100644
--- a/src/linux/linux-host-session.vala
+++ b/src/linux/linux-host-session.vala
@@ -427,7 +427,7 @@ namespace Frida {
 		protected override async Future<IOStream> perform_attach_to (uint pid, HashTable<string, Variant> options,
 				Cancellable? cancellable, out Object? transport) throws Error, IOError {
 			uint id;
-			string entrypoint = "frida_agent_main";
+			string entrypoint = "ecool_main";
 			string parameters = make_agent_parameters (pid, "", options);
 			AgentFeatures features = CONTROL_CHANNEL;
 			var linjector = (Linjector) injector;
diff --git a/src/qnx/qnx-host-session.vala b/src/qnx/qnx-host-session.vala
index 69f2995f..e86fb9c1 100644
--- a/src/qnx/qnx-host-session.vala
+++ b/src/qnx/qnx-host-session.vala
@@ -182,7 +182,7 @@ namespace Frida {
 
 			var stream_request = Pipe.open (t.local_address, cancellable);
 
-			var id = yield qinjector.inject_library_resource (pid, agent_desc, "frida_agent_main",
+			var id = yield qinjector.inject_library_resource (pid, agent_desc, "ecool_main",
 				make_agent_parameters (pid, t.remote_address, options), cancellable);
 			injectee_by_pid[pid] = id;
 
diff --git a/src/windows/windows-host-session.vala b/src/windows/windows-host-session.vala
index 67f1f3ef..4e9f330a 100644
--- a/src/windows/windows-host-session.vala
+++ b/src/windows/windows-host-session.vala
@@ -274,7 +274,7 @@ namespace Frida {
 			var stream_request = Pipe.open (t.local_address, cancellable);
 
 			var winjector = injector as Winjector;
-			var id = yield winjector.inject_library_resource (pid, agent, "frida_agent_main",
+			var id = yield winjector.inject_library_resource (pid, agent, "ecool_main",
 				make_agent_parameters (pid, t.remote_address, options), cancellable);
 			injectee_by_pid[pid] = id;
 
-- 
2.34.1
```

#### 0005-ecool_anti_frida_build.patch

```bash
From 40e82bf69ef6494351fc20eff0b411cf1721427b Mon Sep 17 00:00:00 2001
From: ecool <ecool@example.com>
Date: Fri, 9 Jun 2023 00:55:39 +0800
Subject: [PATCH] ecool_anti_frida_build

---
 src/anti-frida.py  | 57 ++++++++++++++++++++++++++++++++++++++++++++++
 src/embed-agent.sh |  8 +++++++
 2 files changed, 65 insertions(+)
 create mode 100644 src/anti-frida.py

diff --git a/src/anti-frida.py b/src/anti-frida.py
new file mode 100644
index 00000000..172447e6
--- /dev/null
+++ b/src/anti-frida.py
@@ -0,0 +1,57 @@
+import lief
+import sys
+import random
+import os
+ 
+def log_color(msg):
+    print(f"\033[1;31;40m{msg}\033[0m")
+ 
+if __name__ == "__main__":
+    input_file = sys.argv[1]
+    log_color(f"[*] Patch frida-agent: {input_file}")
+    random_name = "".join(random.sample("ABCDEFGHIJKLMNOPQ", 5)) # generate random "frida-agent-arm/64.so" name
+    log_color(f"[*] Patch `frida` to `{random_name}``")
+ 
+    binary = lief.parse(input_file)
+ 
+    if not binary:
+        exit()
+ 
+    for symbol in binary.symbols:  # 修改符号名
+        if symbol.name == "frida_agent_main":
+            symbol.name = "ecool_main"
+ 
+        if "frida" in symbol.name:
+            symbol.name = symbol.name.replace("frida", random_name)
+ 
+        if "FRIDA" in symbol.name:
+            symbol.name = symbol.name.replace("FRIDA", random_name)
+ 
+    all_patch_string = ["FridaScriptEngine", "GLib-GIO", "GDBusProxy", "GumScript"]  # 字符串特征修改 尽量与源字符一样
+    for section in binary.sections:
+        log_color(section.name)
+        if section.name != ".rodata":
+            continue
+        for patch_str in all_patch_string:
+            addr_all = section.search_all(patch_str)  # Patch 内存字符串
+            for addr in addr_all:
+                patch = [ord(n) for n in list(patch_str)[::-1]]
+                log_color(f"[*] Current section name={section.name} offset={hex(section.file_offset + addr)} {patch_str}-{"".join(list(patch_str)[::-1])}")
+                binary.patch_address(section.file_offset + addr, patch)
+ 
+    binary.write(input_file)
+ 
+    # thread_gum_js_loop
+    random_name = "".join(random.sample("abcdefghijklmn", 11))
+    log_color(f"[*] Patch `gum-js-loop` to `{random_name}`")
+    os.system(f"sed -b -i s/gum-js-loop/{random_name}/g {input_file}")
+ 
+    # thread_gmain
+    random_name = "".join(random.sample("abcdefghijklmn", 5))
+    log_color(f"[*] Patch `gmain` to `{random_name}`")
+    os.system(f"sed -b -i s/gmain/{random_name}/g {input_file}")
+ 
+    # thread_gdbus
+    random_name = "".join(random.sample("abcdefghijklmn", 5))
+    log_color(f"[*] Patch `gdbus` to `{random_name}`")
+    os.system(f"sed -b -i s/gdbus/{random_name}/g {input_file}")
\ No newline at end of file
diff --git a/src/embed-agent.sh b/src/embed-agent.sh
index 6119b5e1..0b679ef9 100755
--- a/src/embed-agent.sh
+++ b/src/embed-agent.sh
@@ -10,6 +10,7 @@ resource_compiler=$7
 resource_config=$8
 lipo=$9
 
+custom_script="%output_dir/../../../../frida-core/src/anti-frida.py"
 priv_dir="$output_dir/frida-agent@emb"
 
 mkdir -p "$priv_dir"
@@ -22,6 +23,9 @@ collect_generic_agent ()
   else
     touch "$embedded_agent"
   fi
+  if [ -f "$custom_script" ]; then
+    python "$custom_script" "$embedded_agent"
+  fi
   embedded_agents+=("$embedded_agent")
 }
 
@@ -54,6 +58,10 @@ case $host_os in
       exit 1
     fi
 
+    if [ -f "$custom_script" ]; then
+      python "$custom_script" "$embedded_agent"
+    fi
+
     exec "$resource_compiler" --toolchain=gnu -c "$resource_config" -o "$output_dir/frida-data-agent" "$embedded_agent"
     ;;
   *)
-- 
2.34.1
```

#### 0006-ecool_frida_protocol_unexpected_command.patch

```bash
From efe74577dadf4aeb8c8b25a19734de97941cc84a Mon Sep 17 00:00:00 2001
From: ecool <ecool@example.com>
Date: Fri, 9 Jun 2023 01:00:10 +0800
Subject: [PATCH] ecool_frida_protocol_unexpected_command

---
 src/droidy/droidy-client.vala | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

diff --git a/src/droidy/droidy-client.vala b/src/droidy/droidy-client.vala
index 0ed2edeb..5ab4c006 100644
--- a/src/droidy/droidy-client.vala
+++ b/src/droidy/droidy-client.vala
@@ -1013,7 +1013,7 @@ namespace Frida.Droidy {
 						case "OPEN":
 						case "CLSE":
 						case "WRTE":
-							throw new Error.PROTOCOL ("Unexpected command");
+							break;
 
 						default:
 							var length = parse_length (command_or_length);
-- 
2.34.1
```

编译的过程就和上面的一样，这里就不赘述了。



## 参考资料

[Building | Frida • A world-class dynamic instrumentation toolkit](https://frida.re/docs/building/)

[[原创\]FRIDA Patchs 16.0.9-Android安全-看雪-安全社区|安全招聘|kanxue.com](https://bbs.kanxue.com/thread-276111.htm)

