---
title: Linux内核监控与攻防应用笔记
slug: technology/android/kernel/discussion-18/
url: https://github.com/jygzyc/notes/discussions/18
date: 2024-05-30
authors: [jygzyc]
categories: 
  - 0101-Android
labels: ['010104-Kernel']
comments: true
---

<!-- note_linux_tracing_systems -->

> 这篇文章主要参考了[Linux 内核监控在 Android 攻防中的应用](https://evilpan.com/2022/01/03/kernel-tracing/)，自用笔记

## Kernel Tracing System 101

之前听说过很多内核中的监控方案，包括 strace，ltrace，KProbes，JProbes、uprobe、eBPF、tracefs、systemtab 等等，到底他们之间的的关系是什么，分别都有什么用呢。以及他们后续能否被用来作为攻防的输入。根据这篇文章[^1]中的介绍，我们可以将其分为三个部分：

- 数据源: 根据监控数据的来源划分，包括探针和断点两类
- 采集机制: 根据内核提供给用户态的原始事件回调接口进行划分
- 前端: 获取和解析监控事件数据的用户工具

![Fig1](https://raw.githubusercontent.com/jygzyc/notes-images/main/note_linux_tracing_systems-2024-05-30-23-38-41.png)

在开始介绍之前，先来看看我们能在内核监控到什么？

- 系统调用
- Linux 内核函数调用（例如，TCP 堆栈中的哪些函数正在被调用？）
- 用户空间函数调用（`malloc` 是否被调用？）
- 用户空间或内核中的自定义“**事件**”

以上这些都是可能实现的，但是事实上追踪这些也是非常复杂的，下面就来一一进行说明。

### Data source：KProbes

KProbes 是 Linux 内核的一种调试机制，也可用于监视生产系统内的事件。简单来说，KProbes 可以实现动态内核的注入，基于中断的方法在任意指令中插入追踪代码，并且通过 pre_handler/post_handler/fault_handler 去接收回调。[^2]

#### Example

一个[官方案例](https://elixir.bootlin.com/linux/latest/source/samples/kprobes/kprobe_example.c)如下

```c++
/ SPDX-License-Identifier: GPL-2.0-only
/*
 * Here's a sample kernel module showing the use of kprobes to dump a
 * stack trace and selected registers when kernel_clone() is called.
 *
 * For more information on theory of operation of kprobes, see
 * Documentation/trace/kprobes.rst
 *
 * You will see the trace data in /var/log/messages and on the console
 * whenever kernel_clone() is invoked to create a new process.
 */

#define pr_fmt(fmt) "%s: " fmt, __func__

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/kprobes.h>

static char symbol[KSYM_NAME_LEN] = "kernel_clone";
module_param_string(symbol, symbol, KSYM_NAME_LEN, 0644);

/* For each probe you need to allocate a kprobe structure */
static struct kprobe kp = {
	.symbol_name	= symbol,
};

/* kprobe pre_handler: called just before the probed instruction is executed */
static int __kprobes handler_pre(struct kprobe *p, struct pt_regs *regs)
{
#ifdef CONFIG_X86
	pr_info("<%s> p->addr = 0x%p, ip = %lx, flags = 0x%lx\n",
		p->symbol_name, p->addr, regs->ip, regs->flags);
#endif
#ifdef CONFIG_PPC
	pr_info("<%s> p->addr = 0x%p, nip = 0x%lx, msr = 0x%lx\n",
		p->symbol_name, p->addr, regs->nip, regs->msr);
#endif
#ifdef CONFIG_MIPS
	pr_info("<%s> p->addr = 0x%p, epc = 0x%lx, status = 0x%lx\n",
		p->symbol_name, p->addr, regs->cp0_epc, regs->cp0_status);
#endif
#ifdef CONFIG_ARM64
	pr_info("<%s> p->addr = 0x%p, pc = 0x%lx, pstate = 0x%lx\n",
		p->symbol_name, p->addr, (long)regs->pc, (long)regs->pstate);
#endif
#ifdef CONFIG_ARM
	pr_info("<%s> p->addr = 0x%p, pc = 0x%lx, cpsr = 0x%lx\n",
		p->symbol_name, p->addr, (long)regs->ARM_pc, (long)regs->ARM_cpsr);
#endif
#ifdef CONFIG_RISCV
	pr_info("<%s> p->addr = 0x%p, pc = 0x%lx, status = 0x%lx\n",
		p->symbol_name, p->addr, regs->epc, regs->status);
#endif
#ifdef CONFIG_S390
	pr_info("<%s> p->addr, 0x%p, ip = 0x%lx, flags = 0x%lx\n",
		p->symbol_name, p->addr, regs->psw.addr, regs->flags);
#endif
#ifdef CONFIG_LOONGARCH
	pr_info("<%s> p->addr = 0x%p, era = 0x%lx, estat = 0x%lx\n",
		p->symbol_name, p->addr, regs->csr_era, regs->csr_estat);
#endif

	/* A dump_stack() here will give a stack backtrace */
	return 0;
}

/* kprobe post_handler: called after the probed instruction is executed */
static void __kprobes handler_post(struct kprobe *p, struct pt_regs *regs,
				unsigned long flags)
{
#ifdef CONFIG_X86
	pr_info("<%s> p->addr = 0x%p, flags = 0x%lx\n",
		p->symbol_name, p->addr, regs->flags);
#endif
#ifdef CONFIG_PPC
	pr_info("<%s> p->addr = 0x%p, msr = 0x%lx\n",
		p->symbol_name, p->addr, regs->msr);
#endif
#ifdef CONFIG_MIPS
	pr_info("<%s> p->addr = 0x%p, status = 0x%lx\n",
		p->symbol_name, p->addr, regs->cp0_status);
#endif
#ifdef CONFIG_ARM64
	pr_info("<%s> p->addr = 0x%p, pstate = 0x%lx\n",
		p->symbol_name, p->addr, (long)regs->pstate);
#endif
#ifdef CONFIG_ARM
	pr_info("<%s> p->addr = 0x%p, cpsr = 0x%lx\n",
		p->symbol_name, p->addr, (long)regs->ARM_cpsr);
#endif
#ifdef CONFIG_RISCV
	pr_info("<%s> p->addr = 0x%p, status = 0x%lx\n",
		p->symbol_name, p->addr, regs->status);
#endif
#ifdef CONFIG_S390
	pr_info("<%s> p->addr, 0x%p, flags = 0x%lx\n",
		p->symbol_name, p->addr, regs->flags);
#endif
#ifdef CONFIG_LOONGARCH
	pr_info("<%s> p->addr = 0x%p, estat = 0x%lx\n",
		p->symbol_name, p->addr, regs->csr_estat);
#endif
}

static int __init kprobe_init(void)
{
	int ret;
	kp.pre_handler = handler_pre;
	kp.post_handler = handler_post;

	ret = register_kprobe(&kp);
	if (ret < 0) {
		pr_err("register_kprobe failed, returned %d\n", ret);
		return ret;
	}
	pr_info("Planted kprobe at %p\n", kp.addr);
	return 0;
}

static void __exit kprobe_exit(void)
{
	unregister_kprobe(&kp);
	pr_info("kprobe at %p unregistered\n", kp.addr);
}

module_init(kprobe_init)
module_exit(kprobe_exit)
MODULE_LICENSE("GPL");
```

上述的案例中，每当系统中进程调用`kernel_clone()`，就会触发`handler`，从而在`dmesg`中输出堆栈和寄存器的信息。同时也可以看出，为了兼容不同的系统架构，这里的模块案例做了不同的处理。



#### 原理

[^1]: [Linux tracing systems & how they fit together](https://jvns.ca/blog/2017/07/05/linux-tracing-systems/)
[^2]: [Linux 内核监控在 Android 攻防中的应用](https://evilpan.com/2022/01/03/kernel-tracing/)
[^3]: [An introduction to KProbes](https://lwn.net/Articles/132196/)
[^4]: [Kernel Probes (Kprobes)](https://www.kernel.org/doc/html/latest/trace/kprobes.html)
  
<script src="https://giscus.app/client.js"
    data-repo="jygzyc/notes"
    data-repo-id="R_kgDOJrOxMQ"
    data-mapping="number"
    data-term="18"
    data-reactions-enabled="1"
    data-emit-metadata="0"
    data-input-position="top"
    data-theme="preferred_color_scheme"
    data-lang="zh-CN"
    crossorigin="anonymous"
    async>
</script>
