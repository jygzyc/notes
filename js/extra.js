
// 消除控制台打印
var HoldLog = console.log;
console.log = function() {};
let now1 = new Date();
queueMicrotask( () => {
    const Log = function() {
        HoldLog.apply(console, arguments);
    };
    //在恢复前输出日志
    const grt = new Date("01/01/2022 00:00:00");
    //此处修改你的建站时间或者网站上线时间
    now1.setTime(now1.getTime() + 250);
    const days = (now1 - grt) / 1000 / 60 / 60 / 24;
    const dnum = Math.floor(days);
    const ascll = [`欢迎访问Ecool的知识花园!`, `爱自己，每天都要开开心心的哦`, `
███████  ██████  ██████   ██████  ██      
██      ██      ██    ██ ██    ██ ██      
█████   ██      ██    ██ ██    ██ ██      
██      ██      ██    ██ ██    ██ ██      
███████  ██████  ██████   ██████  ███████ 
`, "已上线", dnum, "天", "©2025 By Ecool V1.8.16", ];
    const ascll2 = [`NCC2-036`, `调用前置摄像头拍照成功，识别为【小笨蛋】.`, `Photo captured: `, `🤪`];

    setTimeout(Log.bind(console, `\n%c${ascll[0]} %c ${ascll[1]} %c ${ascll[2]} %c${ascll[3]}%c ${ascll[4]}%c ${ascll[5]}\n\n%c ${ascll[6]}\n`, "color:#425AEF", "", "color:#ff4f87", "color:#425AEF", "", "color:#425AEF", ""));
    setTimeout(Log.bind(console, `%c ${ascll2[0]} %c ${ascll2[1]} %c \n${ascll2[2]} %c\n${ascll2[3]}\n`, "color:white; background-color:#4fd953", "", "", 'background:url("https://npm.elemecdn.com/anzhiyu-blog@1.1.6/img/post/common/tinggge.gif") no-repeat;font-size:450%'));

    setTimeout(Log.bind(console, "%c WELCOME %c 你好，小笨蛋.", "color:white; background-color:#4f90d9", ""));

    setTimeout(console.warn.bind(console, "%c ⚡ Powered by Mkdocs %c 你正在访问 Ecool 的博客.", "color:white; background-color:#f0ad4e", ""));
    setTimeout(console.warn.bind(console, "%c ❶ Blog: %c https://note.lilac.fun", "color:white; background-color:#ff7aa4", ""));
    setTimeout(Log.bind(console, "%c W23-12 %c 你已打开控制台.", "color:white; background-color:#4f90d9", ""));

    setTimeout(console.warn.bind(console, "%c S013-782 %c 你现在正处于监控中，不要干坏事哦.", "color:white; background-color:#d9534f", ""));
});
