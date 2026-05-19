/**
 * Handles the main React medical analysis experience and client-side API flow.
 */

const { useState, useEffect } = React;

const css = `
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&family=Inter:wght@400;500;600&display=swap');
*{margin:0;padding:0;box-sizing:border-box;}
html{scroll-behavior:smooth;}
.sr{font-family:'Inter',sans-serif;background:#f0f4ff;color:#0f172a;overflow-x:hidden;}

/* NAV */
.nav{position:sticky;top:0;z-index:100;background:rgba(8,14,32,0.94);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,0.07);display:flex;align-items:center;justify-content:space-between;padding:14px 56px;transition:background .3s;}
.nav-brand{display:flex;align-items:center;gap:12px;cursor:pointer;}
.nav-logo{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#3b82f6,#06b6d4);display:flex;align-items:center;justify-content:center;animation:pulseglow 3s ease-in-out infinite;}
@keyframes pulseglow{0%,100%{box-shadow:0 0 18px rgba(59,130,246,.4)}50%{box-shadow:0 0 38px rgba(6,182,212,.75)}}
.nav-name{font-family:'Outfit',sans-serif;font-weight:900;font-size:22px;color:#fff;letter-spacing:-0.5px;}
.nav-sub{font-size:11px;color:rgba(255,255,255,.38);margin-top:1px;}
.nav-links{display:flex;gap:6px;}
.nav-link{font-size:13px;color:rgba(255,255,255,.55);cursor:pointer;padding:8px 16px;border-radius:8px;transition:color .2s,background .2s;text-decoration:none;border:none;background:transparent;}
.nav-link:hover{color:#fff;background:rgba(255,255,255,.08);}
.nav-link.active{color:#60a5fa;background:rgba(59,130,246,.12);}
.nav-cta{padding:10px 24px;border-radius:50px;background:linear-gradient(90deg,#3b82f6,#06b6d4);color:#fff;font-size:13px;font-weight:700;border:none;cursor:pointer;transition:transform .15s,box-shadow .2s;}
.nav-cta:hover{transform:scale(1.04);box-shadow:0 0 24px rgba(6,182,212,.6);}

/* HERO */
.hero{min-height:92vh;display:grid;grid-template-columns:1fr 1fr;align-items:center;padding:0 80px;background:linear-gradient(135deg,#080f24 0%,#0b1a38 55%,#071e3d 100%);position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 15% 50%,rgba(59,130,246,.18) 0%,transparent 60%),radial-gradient(ellipse at 85% 20%,rgba(6,182,212,.14) 0%,transparent 60%);}
.particles{position:absolute;inset:0;pointer-events:none;}
.pt{position:absolute;border-radius:50%;background:rgba(59,130,246,.25);animation:floatup linear infinite;}
@keyframes floatup{0%{transform:translateY(105vh) scale(0);opacity:0}10%{opacity:1}90%{opacity:.2}100%{transform:translateY(-30px) scale(1);opacity:0}}
.hero-left{position:relative;z-index:2;padding:80px 0;}
.hero-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(59,130,246,.14);border:1px solid rgba(59,130,246,.28);border-radius:50px;padding:7px 18px;margin-bottom:28px;animation:fadeup .6s ease both;}
.bdot{width:8px;height:8px;border-radius:50%;background:#3b82f6;animation:blink 1.5s infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
.btxt{font-size:12px;color:#93c5fd;font-weight:600;letter-spacing:.5px;}
.h1{font-family:'Outfit',sans-serif;font-weight:900;font-size:clamp(36px,4vw,56px);line-height:1.1;color:#fff;margin-bottom:20px;animation:fadeup .7s .1s ease both;}
.h1 span{background:linear-gradient(90deg,#60a5fa,#34d399);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.desc{font-size:15px;color:rgba(255,255,255,.58);line-height:1.75;max-width:480px;margin-bottom:36px;animation:fadeup .7s .2s ease both;}
@keyframes fadeup{from{opacity:0;transform:translateY(28px)}to{opacity:1;transform:translateY(0)}}
.hero-form{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:20px;padding:28px;backdrop-filter:blur(12px);animation:fadeup .7s .3s ease both;}
.f-lbl{font-size:13px;color:rgba(255,255,255,.48);display:block;margin-bottom:10px;}
.f-ta{width:100%;min-height:108px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.13);border-radius:12px;padding:14px 16px;color:#fff;font-size:14px;font-family:'Inter',sans-serif;resize:none;outline:none;line-height:1.6;transition:border-color .2s,background .2s;}
.f-ta::placeholder{color:rgba(255,255,255,.26);}
.f-ta:focus{border-color:rgba(99,179,237,.5);background:rgba(255,255,255,.1);}
.f-btn{margin-top:14px;width:100%;padding:15px;border:none;border-radius:12px;background:linear-gradient(90deg,#2563eb,#06b6d4);color:#fff;font-size:15px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:10px;transition:transform .15s,box-shadow .2s;position:relative;overflow:hidden;}
.f-btn:disabled{opacity:.75;cursor:not-allowed;transform:none;box-shadow:none;}
.f-btn:hover{transform:translateY(-2px);box-shadow:0 10px 32px rgba(6,182,212,.5);}
.f-btn::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.17),transparent);transform:translateX(-100%);transition:transform .55s;}
.f-btn:hover::after{transform:translateX(100%);}
.api-msg{margin-top:14px;padding:12px 14px;border-radius:12px;font-size:13px;line-height:1.45;}
.api-msg.err{background:rgba(239,68,68,.16);border:1px solid rgba(239,68,68,.45);color:#fecaca;}
.api-res{margin-top:14px;padding:16px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);border-radius:12px;color:#e2e8f0;}
.api-res h4{margin:0 0 8px;font-size:15px;color:#fff;}
.api-res p{margin:0 0 5px;font-size:13px;color:#cbd5e1;}
.api-list{margin:8px 0 0;padding-left:18px;}
.api-list li{font-size:12px;color:#bfdbfe;margin-bottom:4px;}
.internal-panel{margin-top:16px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);border-radius:14px;padding:14px;}
.internal-title{font-size:14px;font-weight:700;color:#fff;margin-bottom:8px;}
.internal-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:8px;}
.detail-btn{border:1px solid rgba(148,163,184,.55);background:rgba(30,41,59,.55);color:#cbd5e1;padding:6px 10px;border-radius:8px;font-size:11px;font-weight:600;cursor:pointer;}
.detail-btn:hover{background:rgba(51,65,85,.65);}
.tok-wrap{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;}
.tok{font-size:11px;padding:6px 10px;border-radius:999px;border:1px solid rgba(255,255,255,.2);background:rgba(15,23,42,.45);color:#e2e8f0;}
.tok.sym{background:rgba(16,185,129,.2);border-color:rgba(16,185,129,.45);color:#bbf7d0;}
.tok.neg{background:rgba(244,63,94,.2);border-color:rgba(244,63,94,.45);color:#fecdd3;}
.tok.int{background:rgba(245,158,11,.2);border-color:rgba(245,158,11,.45);color:#fde68a;}
.tok.time{background:rgba(59,130,246,.2);border-color:rgba(59,130,246,.45);color:#bfdbfe;}
.mini-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-bottom:10px;}
.mini-stat{background:rgba(15,23,42,.35);border:1px solid rgba(255,255,255,.15);border-radius:10px;padding:8px;}
.mini-stat b{display:block;color:#fff;font-size:14px;}
.mini-stat span{font-size:11px;color:#cbd5e1;}
.syntax-table{width:100%;border-collapse:collapse;background:rgba(15,23,42,.35);border-radius:10px;overflow:hidden;}
.syntax-table th,.syntax-table td{font-size:11px;padding:7px 8px;text-align:left;color:#e2e8f0;border-bottom:1px solid rgba(255,255,255,.08);}
.syntax-table th{font-size:10px;letter-spacing:.4px;text-transform:uppercase;color:#bfdbfe;background:rgba(30,41,59,.55);}
.pos-pill{display:inline-flex;align-items:center;justify-content:center;min-width:44px;padding:3px 8px;border-radius:999px;font-size:10px;font-weight:700;}
.pos-verb{background:rgba(245,158,11,.22);color:#fde68a;border:1px solid rgba(245,158,11,.4);}
.pos-nom{background:rgba(16,185,129,.22);color:#bbf7d0;border:1px solid rgba(16,185,129,.4);}
.pos-det{background:rgba(59,130,246,.22);color:#bfdbfe;border:1px solid rgba(59,130,246,.4);}
.pos-adv{background:rgba(168,85,247,.22);color:#ddd6fe;border:1px solid rgba(168,85,247,.4);}
.pos-default{background:rgba(148,163,184,.2);color:#e2e8f0;border:1px solid rgba(148,163,184,.35);}
.tree-box{margin-top:10px;background:rgba(15,23,42,.35);border:1px solid rgba(255,255,255,.15);border-radius:10px;padding:8px;color:#bfdbfe;font-size:11px;white-space:pre-wrap;}
.api-top10{margin-top:18px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:16px;padding:18px;}
.api-top10 h3{font-size:18px;font-weight:800;color:#0f172a;margin-bottom:6px;}
.api-top10 p{font-size:13px;color:#64748b;margin-bottom:10px;}
.api-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;}
.api-card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:12px;}
.api-card h4{font-size:14px;color:#0f172a;margin:0 0 4px;}
.api-card small{display:block;color:#475569;font-size:11px;margin-bottom:4px;}
.api-card span{font-size:11px;color:#64748b;line-height:1.4;display:block;}

@media (max-width: 760px){
  .api-grid{grid-template-columns:1fr;}
}
.hero-right{position:relative;z-index:2;display:flex;align-items:center;justify-content:center;padding:60px 0 60px 40px;animation:fadein-r .9s .2s ease both;}
@keyframes fadein-r{from{opacity:0;transform:translateX(40px)}to{opacity:1;transform:translateX(0)}}
.illus{position:relative;width:420px;height:470px;}
.illus-main{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:296px;height:370px;border-radius:28px;background:linear-gradient(145deg,#162d55,#0d1f3c);border:1px solid rgba(59,130,246,.28);overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.5);}
.illus-inner{width:100%;height:100%;background:linear-gradient(160deg,#192f5a 0%,#0c2044 40%,#071832 100%);display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;}
.illus-glow{position:absolute;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,rgba(59,130,246,.2) 0%,transparent 70%);top:50px;left:50%;transform:translateX(-50%);}
.pill{position:absolute;border-radius:14px;padding:10px 16px;backdrop-filter:blur(8px);display:flex;align-items:center;gap:8px;}
.pill-1{top:28px;right:-12px;background:rgba(16,185,129,.14);border:1px solid rgba(16,185,129,.32);animation:floaty 4s ease-in-out infinite;}
.pill-2{bottom:70px;left:-22px;background:rgba(59,130,246,.14);border:1px solid rgba(59,130,246,.32);animation:floaty 5s 1s ease-in-out infinite;}
.pill-3{top:130px;right:-28px;background:rgba(139,92,246,.14);border:1px solid rgba(139,92,246,.32);animation:floaty 3.5s .5s ease-in-out infinite;}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.pill-name{font-size:12px;font-weight:700;color:#fff;}
.pill-info{font-size:10px;color:rgba(255,255,255,.48);}

/* STATS */
.stats-bar{background:#fff;border-bottom:1px solid #e8edf5;display:grid;grid-template-columns:repeat(4,1fr);}
.stat-item{padding:28px 0;text-align:center;border-right:1px solid #e8edf5;transition:background .2s;}
.stat-item:last-child{border-right:none;}
.stat-item:hover{background:#f5f9ff;}
.stat-num{font-family:'Outfit',sans-serif;font-size:30px;font-weight:900;margin-top:10px;}
.stat-lbl{font-size:13px;color:#64748b;margin-top:3px;}

/* HOW */
.how-sec{padding:100px 80px;background:linear-gradient(135deg,#1e40af 0%,#0369a1 55%,#0891b2 100%);position:relative;overflow:hidden;}
.how-sec::before{content:'';position:absolute;top:-80px;right:-80px;width:360px;height:360px;border-radius:50%;background:rgba(255,255,255,.05);}
.how-sec::after{content:'';position:absolute;bottom:-100px;left:-60px;width:300px;height:300px;border-radius:50%;background:rgba(255,255,255,.04);}
.sec-hdr{text-align:center;margin-bottom:64px;}
.sec-ttl{font-family:'Outfit',sans-serif;font-weight:900;font-size:42px;color:#fff;margin-bottom:10px;}
.sec-sub{font-size:16px;color:rgba(255,255,255,.62);}
.sec-ttl-dk{font-family:'Outfit',sans-serif;font-weight:900;font-size:42px;color:#0f172a;margin-bottom:10px;}
.sec-sub-dk{font-size:16px;color:#64748b;}
.blu{background:linear-gradient(90deg,#2563eb,#0891b2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.steps-row{display:flex;align-items:stretch;position:relative;z-index:1;max-width:1040px;margin:0 auto;}
.step-card{flex:1;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.17);border-radius:20px;padding:36px 28px;transition:transform .25s,background .25s,box-shadow .25s;}
.step-card:hover{transform:translateY(-7px);background:rgba(255,255,255,.18);box-shadow:0 22px 60px rgba(0,0,0,.22);}
.sn{font-family:'Outfit',sans-serif;font-size:52px;font-weight:900;color:rgba(255,255,255,.18);line-height:1;}
.st{font-size:16px;font-weight:700;color:#fff;margin:14px 0 6px;}
.ss{font-size:13px;color:rgba(255,255,255,.58);}
.sarr{display:flex;align-items:center;padding:0 16px;color:rgba(255,255,255,.3);font-size:26px;flex-shrink:0;}

/* FEATURES */
.feat-sec{padding:100px 80px;background:#f0f4ff;}
.feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;max-width:1040px;margin:0 auto;}
.feat-card{background:#fff;border-radius:22px;padding:38px 32px;border:1px solid #e8edf5;transition:transform .25s,box-shadow .25s,border-color .25s;position:relative;overflow:hidden;}
.feat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;opacity:0;transition:opacity .25s;}
.feat-card:nth-child(1)::before{background:linear-gradient(90deg,#2563eb,#60a5fa);}
.feat-card:nth-child(2)::before{background:linear-gradient(90deg,#059669,#34d399);}
.feat-card:nth-child(3)::before{background:linear-gradient(90deg,#7c3aed,#c084fc);}
.feat-card:hover{transform:translateY(-8px);box-shadow:0 24px 60px rgba(0,0,0,.09);border-color:transparent;}
.feat-card:hover::before{opacity:1;}
.fi{width:56px;height:56px;border-radius:16px;display:flex;align-items:center;justify-content:center;margin-bottom:22px;}
.ft{font-family:'Outfit',sans-serif;font-size:20px;font-weight:700;color:#0f172a;margin-bottom:12px;}
.fd{font-size:14px;color:#64748b;line-height:1.75;}

/* === CREATIVE DISEASE SECTION === */
.dis-sec{padding:100px 80px;background:#fff;}
.body-explorer{max-width:1040px;margin:0 auto;}
.body-tabs{display:flex;gap:10px;justify-content:center;margin-bottom:48px;flex-wrap:wrap;}
.body-tab{padding:10px 22px;border-radius:50px;border:1.5px solid #e2e8f0;background:#fff;font-size:13px;font-weight:600;color:#64748b;cursor:pointer;transition:all .2s;display:flex;align-items:center;gap:8px;}
.body-tab:hover{border-color:#93c5fd;color:#2563eb;background:#eff6ff;}
.body-tab.sel{background:linear-gradient(90deg,#2563eb,#0891b2);border-color:transparent;color:#fff;box-shadow:0 6px 24px rgba(37,99,235,.35);}
.body-tab.sel svg{stroke:#fff;}
.cat-panel{display:grid;grid-template-columns:1fr 1fr;gap:32px;align-items:start;animation:fadeup .4s ease both;}
.cat-left{position:relative;}
.cat-big-card{border-radius:24px;padding:40px 38px;color:#fff;position:relative;overflow:hidden;min-height:280px;display:flex;flex-direction:column;justify-content:space-between;}
.cat-big-card::before{content:'';position:absolute;top:-60px;right:-60px;width:220px;height:220px;border-radius:50%;background:rgba(255,255,255,.08);}
.cat-big-card::after{content:'';position:absolute;bottom:-40px;left:-40px;width:160px;height:160px;border-radius:50%;background:rgba(255,255,255,.06);}
.cat-icon-big{width:72px;height:72px;border-radius:20px;background:rgba(255,255,255,.15);display:flex;align-items:center;justify-content:center;margin-bottom:20px;position:relative;z-index:1;}
.cat-name{font-family:'Outfit',sans-serif;font-size:28px;font-weight:900;margin-bottom:8px;position:relative;z-index:1;}
.cat-count{font-size:14px;opacity:.72;position:relative;z-index:1;}
.cat-bar{width:60px;height:3px;border-radius:2px;background:rgba(255,255,255,.4);margin-top:24px;position:relative;z-index:1;}
.cat-right{display:flex;flex-direction:column;gap:12px;}
.dis-mini-card{background:#f8faff;border:1.5px solid #e8edf5;border-radius:14px;padding:16px 20px;display:flex;align-items:center;gap:14px;transition:all .22s;cursor:default;}
.dis-mini-card:hover{background:#eff6ff;border-color:#93c5fd;transform:translateX(6px);}
.dis-mini-icon{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.dis-mini-name{font-size:14px;font-weight:700;color:#1e293b;}
.dis-mini-sub{font-size:12px;color:#94a3b8;margin-top:2px;}
.dis-counter{text-align:center;margin-top:48px;padding:28px;background:#f0f4ff;border-radius:20px;}
.dis-counter-num{font-family:'Outfit',sans-serif;font-size:48px;font-weight:900;background:linear-gradient(90deg,#2563eb,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.dis-counter-lbl{font-size:15px;color:#64748b;margin-top:4px;}

/* CTA */
.cta-sec{padding:0 80px 100px;background:#fff;}
.cta-card{max-width:1040px;margin:0 auto;background:linear-gradient(135deg,#1d4ed8 0%,#0369a1 50%,#0891b2 100%);border-radius:28px;padding:80px 64px;display:flex;align-items:center;justify-content:space-between;gap:48px;position:relative;overflow:hidden;}
.cta-card::after{content:'';position:absolute;right:-100px;top:-100px;width:360px;height:360px;border-radius:50%;background:rgba(255,255,255,.06);}
.ct{position:relative;z-index:1;}
.ctt{font-family:'Outfit',sans-serif;font-size:40px;font-weight:900;color:#fff;margin-bottom:12px;}
.cts{font-size:16px;color:rgba(255,255,255,.7);max-width:500px;line-height:1.6;}
.ctabtn{flex-shrink:0;background:#fff;border:none;border-radius:50px;padding:18px 44px;font-size:15px;font-weight:700;color:#1d4ed8;cursor:pointer;display:flex;align-items:center;gap:10px;transition:transform .15s,box-shadow .2s;white-space:nowrap;position:relative;z-index:1;}
.ctabtn:hover{transform:scale(1.05);box-shadow:0 12px 40px rgba(0,0,0,.2);}

/* FOOTER */
.footer{background:#080f24;border-top:1px solid rgba(255,255,255,.07);padding:48px 80px 32px;display:flex;flex-direction:column;align-items:center;gap:18px;}
.fbrand{display:flex;align-items:center;gap:12px;}
.flogo{width:40px;height:40px;border-radius:11px;background:linear-gradient(135deg,#3b82f6,#06b6d4);display:flex;align-items:center;justify-content:center;}
.fname{font-family:'Outfit',sans-serif;font-size:20px;font-weight:900;color:#fff;}
.ftag{font-size:13px;color:rgba(255,255,255,.36);text-align:center;}
.fdiv{width:100%;max-width:420px;height:1px;background:rgba(255,255,255,.07);}
.fcpy{font-size:12px;color:#ffffff26;}

/* STYLES AMÉLIORÉS POUR L'ANALYSE SYNTAXIQUE */
.internal-panel{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:20px;margin-top:16px;backdrop-filter:blur(8px);}
.internal-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,.1);}
.internal-title{font-size:16px;font-weight:700;color:#fff;display:flex;align-items:center;gap:8px;}
.detail-btn{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);color:#fff;padding:6px 12px;border-radius:8px;font-size:12px;cursor:pointer;transition:all .2s;}
.detail-btn:hover{background:rgba(255,255,255,.2);}

.analysis-section{margin-bottom:24px;}
.section-title{font-size:14px;font-weight:600;color:#93c5fd;margin-bottom:12px;display:flex;align-items:center;gap:6px;}
.syntax-info{margin-bottom:12px;}
.syntax-info p{font-size:12px;color:rgba(255,255,255,.7);margin:0;}

.tok-wrap{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px;padding:12px;background:rgba(0,0,0,.2);border-radius:8px;}
.tok{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);padding:4px 8px;border-radius:6px;font-size:12px;color:#fff;display:flex;align-items:center;gap:4px;transition:all .2s;cursor:default;}
.tok:hover{background:rgba(255,255,255,.2);transform:scale(1.05);}
.tok.sym{background:rgba(34,197,94,.2);border-color:rgba(34,197,94,.4);}
.tok.neg{background:rgba(239,68,68,.2);border-color:rgba(239,68,68,.4);}
.tok.int{background:rgba(251,146,60,.2);border-color:rgba(251,146,60,.4);}
.tok.word{background:rgba(107,114,128,.2);border-color:rgba(107,114,128,.4);}
.token-type{font-size:10px;background:rgba(0,0,0,.3);padding:1px 4px;border-radius:3px;color:#93c5ff;}

.mini-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px;}
.mini-stat{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:12px;text-align:center;transition:all .2s;}
.mini-stat:hover{background:rgba(255,255,255,.1);transform:translateY(-2px);}
.stat-number{font-size:18px;font-weight:700;color:#fff;margin-bottom:4px;}
.stat-label{font-size:11px;color:rgba(255,255,255,.6);}
.stat-symptom{background:rgba(34,197,94,.1);border-color:rgba(34,197,94,.3);}
.stat-symptom .stat-number{color:#22c55e;}
.stat-negation{background:rgba(239,68,68,.1);border-color:rgba(239,68,68,.3);}
.stat-negation .stat-number{color:#ef4444;}
.stat-intensifier{background:rgba(251,146,60,.1);border-color:rgba(251,146,60,.3);}
.stat-intensifier .stat-number{color:#fb923c;}

.syntax-table{width:100%;border-collapse:collapse;background:rgba(0,0,0,.2);border-radius:8px;overflow:hidden;}
.syntax-table th{background:rgba(255,255,255,.1);color:#fff;font-size:12px;font-weight:600;padding:10px;text-align:left;}
.syntax-table td{padding:8px 10px;font-size:12px;color:rgba(255,255,255,.9);border-top:1px solid rgba(255,255,255,.05);}
.syntax-row:hover{background:rgba(255,255,255,.05);}
.word-cell{font-weight:500;}
.pos-pill{padding:2px 6px;border-radius:4px;font-size:10px;font-weight:600;text-transform:uppercase;}
.pos-verb{background:rgba(239,68,68,.2);color:#f87171;}
.pos-nom{background:rgba(34,197,94,.2);color:#4ade80;}
.pos-det{background:rgba(59,130,246,.2);color:#60a5fa;}
.pos-adv{background:rgba(251,146,60,.2);color:#fbbf24;}
.pos-adj{background:rgba(168,85,247,.2);color:#a78bfa;}
.pos-prep{background:rgba(6,182,212,.2);color:#22d3ee;}
.pos-default{background:rgba(107,114,128,.2);color:#9ca3af;}
.role-cell{color:rgba(255,255,255,.7);}
.category-tag{padding:2px 6px;border-radius:4px;font-size:10px;font-weight:500;}
.tag-verb{background:rgba(239,68,68,.15);color:#fca5a5;}
.tag-nom{background:rgba(34,197,94,.15);color:#86efac;}
.tag-det{background:rgba(59,130,246,.15);color:#93c5fd;}
.tag-adv{background:rgba(251,146,60,.15);color:#fcd34d;}
.tag-adj{background:rgba(168,85,247,.15);color:#c4b5fd;}
.tag-prep{background:rgba(6,182,212,.15);color:#67e8f9;}
.tag-default{background:rgba(107,114,128,.15);color:#d1d5db;}

.tree-box{background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:12px;margin-top:12px;}
.tree-box pre{font-family:'Courier New',monospace;font-size:11px;color:#93c5ff;margin:0;white-space:pre-wrap;word-break:break-all;}

/* STYLES POUR LES RÉSULTATS D'ANALYSE SOUS L'IMAGE */
.results-under-doctor{margin-top:40px;padding:0 20px;}
.analysis-results{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:20px;backdrop-filter:blur(10px);}
.results-header{margin-bottom:20px;text-align:center;}
.results-title{font-size:18px;font-weight:700;color:#fff;margin:0;display:flex;align-items:center;justify-content:center;gap:8px;}

.result-card{display:flex;align-items:center;gap:12px;padding:16px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:12px;margin-bottom:16px;transition:all .2s;}
.result-card:hover{background:rgba(255,255,255,.08);transform:translateY(-2px);}
.main-result{background:linear-gradient(135deg,rgba(239,68,68,.1),rgba(220,38,38,.05));border-color:rgba(239,68,68,.2);}
.result-icon{flex-shrink:0;width:40px;height:40px;background:rgba(255,255,255,.1);border-radius:10px;display:flex;align-items:center;justify-content:center;}
.result-content{flex:1;}
.result-label{font-size:12px;color:rgba(255,255,255,.7);margin-bottom:4px;}
.result-value{font-size:16px;font-weight:700;color:#fff;}

.result-stats{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;}
.stat-item{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:10px;padding:12px;}
.stat-item.confidence{background:rgba(34,197,94,.1);border-color:rgba(34,197,94,.2);}
.stat-item.severity{background:rgba(251,146,60,.1);border-color:rgba(251,146,60,.2);}
.stat-label{font-size:11px;color:rgba(255,255,255,.7);margin-bottom:6px;}
.stat-value{font-size:16px;font-weight:700;color:#fff;margin-bottom:8px;}
.stat-bar{width:100%;height:4px;background:rgba(255,255,255,.1);border-radius:2px;overflow:hidden;}
.stat-fill{height:100%;background:linear-gradient(90deg,#22c55e,#16a34a);border-radius:2px;transition:width 0.5s ease;}
.severity-badge{padding:4px 8px;background:rgba(251,146,60,.2);border-radius:6px;font-size:12px;text-align:center;}

.treatment-card{background:rgba(34,197,94,.05);border:1px solid rgba(34,197,94,.15);border-radius:12px;padding:16px;margin-bottom:16px;}
.treatment-header{display:flex;align-items:center;gap:8px;margin-bottom:12px;color:#22c55e;font-size:14px;font-weight:600;}
.treatment-text{font-size:13px;color:rgba(255,255,255,.9);line-height:1.5;}

.other-possibilities{margin-bottom:16px;}
.possibilities-title{font-size:14px;font-weight:600;color:#fff;margin-bottom:12px;}
.possibilities-list{display:flex;flex-direction:column;gap:8px;}
.possibility-item{display:flex;justify-content:space-between;align-items:center;padding:10px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:8px;}
.possibility-name{font-size:13px;color:#fff;font-weight:500;}
.possibility-info{display:flex;gap:8px;}
.prob{font-size:12px;color:#22c55e;font-weight:600;}
.sev{font-size:11px;color:rgba(255,255,255,.6);padding:2px 6px;background:rgba(255,255,255,.1);border-radius:4px;}

.external-matches{margin-bottom:16px;}
.matches-title{font-size:14px;font-weight:600;color:#fff;margin-bottom:12px;}
.matches-list{display:flex;flex-direction:column;gap:8px;}
.match-item{display:flex;justify-content:space-between;align-items:center;padding:8px;background:rgba(59,130,246,.05);border:1px solid rgba(59,130,246,.15);border-radius:6px;}
.match-name{font-size:12px;color:#60a5fa;font-weight:500;}
.match-id{font-size:11px;color:rgba(255,255,255,.5);}

/* STYLES POUR LES RÉSULTATS À LA PLACE DE LA MAQUETTE */
.results-section{padding:60px 80px;background:#fff;}
.results-container{max-width:1200px;margin:0 auto;}
.results-header{text-align:center;margin-bottom:48px;}
.results-main-title{font-family:'Outfit',sans-serif;font-size:42px;font-weight:900;color:#0f172a;margin-bottom:12px;}
.results-subtitle{font-size:18px;color:#64748b;margin:0;}

.results-grid{display:grid;gap:32px;}
.main-result-large{display:flex;align-items:center;gap:20px;padding:32px;background:linear-gradient(135deg,rgba(239,68,68,.05),rgba(220,38,38,.02));border:2px solid rgba(239,68,68,.1);border-radius:20px;transition:all .3s;}
.main-result-large:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(239,68,68,.15);}
.result-icon-large{flex-shrink:0;width:64px;height:64px;background:rgba(239,68,68,.1);border-radius:16px;display:flex;align-items:center;justify-content:center;}
.result-content-large{flex:1;}
.result-label-large{font-size:14px;color:#64748b;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;}
.result-value-large{font-size:28px;font-weight:800;color:#0f172a;line-height:1.2;}

.stats-row{display:grid;grid-template-columns:1fr 1fr;gap:24px;}
.stat-card{display:flex;align-items:center;gap:16px;padding:24px;background:rgba(255,255,255,.8);border:1px solid rgba(0,0,0,.05);border-radius:16px;transition:all .3s;}
.stat-card:hover{transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,0,0,.1);}
.confidence-card{background:linear-gradient(135deg,rgba(34,197,94,.05),rgba(22,163,74,.02));border-color:rgba(34,197,94,.1);}
.severity-card{background:linear-gradient(135deg,rgba(251,146,60,.05),rgba(245,158,11,.02));border-color:rgba(251,146,60,.1);}
.stat-icon{flex-shrink:0;width:48px;height:48px;background:rgba(255,255,255,.9);border-radius:12px;display:flex;align-items:center;justify-content:center;}
.stat-content{flex:1;}
.stat-label{font-size:13px;color:#64748b;margin-bottom:8px;}
.stat-value-large{font-size:24px;font-weight:800;color:#0f172a;margin-bottom:12px;}
.stat-bar-large{width:100%;height:6px;background:rgba(0,0,0,.05);border-radius:3px;overflow:hidden;}
.stat-fill-large{height:100%;background:linear-gradient(90deg,#22c55e,#16a34a);border-radius:3px;transition:width 0.8s ease;}
.severity-badge-large{padding:8px 16px;background:rgba(251,146,60,.1);border:1px solid rgba(251,146,60,.2);border-radius:8px;font-size:14px;font-weight:600;color:#ea580c;text-align:center;}

.treatment-card-large{padding:28px;background:linear-gradient(135deg,rgba(34,197,94,.05),rgba(22,163,74,.02));border:2px solid rgba(34,197,94,.1);border-radius:20px;}
.treatment-header-large{display:flex;align-items:center;gap:12px;margin-bottom:16px;color:#16a34a;font-size:18px;font-weight:700;}
.treatment-text-large{font-size:16px;color:#0f172a;line-height:1.6;}

.other-possibilities-large{margin-top:32px;}
.possibilities-title-large{font-size:24px;font-weight:800;color:#0f172a;margin-bottom:20px;}
.possibilities-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;}
.possibility-card{padding:20px;background:rgba(255,255,255,.8);border:1px solid rgba(0,0,0,.05);border-radius:16px;transition:all .3s;}
.possibility-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.1);}
.possibility-name-large{font-size:18px;font-weight:700;color:#0f172a;margin-bottom:12px;}
.possibility-stats{display:flex;gap:12px;margin-bottom:12px;}
.prob-large{font-size:16px;font-weight:700;color:#16a34a;}
.sev-large{font-size:14px;color:#ea580c;padding:4px 8px;background:rgba(251,146,60,.1);border-radius:6px;}
.possibility-treatment{font-size:14px;color:#64748b;line-height:1.5;}

.external-matches-large{margin-top:32px;}
.matches-title-large{font-size:24px;font-weight:800;color:#0f172a;margin-bottom:20px;}
.matches-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;}
.match-card-large{padding:16px;background:rgba(59,130,246,.05);border:1px solid rgba(59,130,246,.1);border-radius:12px;transition:all .3s;}
.match-card-large:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(59,130,246,.15);}
.match-name-large{font-size:16px;font-weight:600;color:#2563eb;margin-bottom:8px;}
.match-id-large{font-size:13px;color:#64748b;font-family:'Courier New',monospace;}

/* STYLES POUR LES RÉSULTATS DANS LA COLONNE DE DROITE */
.results-right-panel{padding:20px;height:100%;display:flex;flex-direction:column;gap:20px;}
.results-header-right{text-align:center;margin-bottom:20px;}
.results-title-right{font-size:20px;font-weight:700;color:#fff;margin:0 0 8px 0;}
.results-subtitle-right{font-size:14px;color:rgba(255,255,255,.7);margin:0;}

.result-card-right{display:flex;align-items:center;gap:12px;padding:16px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);border-radius:12px;transition:all .2s;}
.result-card-right:hover{background:rgba(255,255,255,.12);transform:translateY(-2px);}
.result-card-right.main{background:linear-gradient(135deg,rgba(239,68,68,.15),rgba(220,38,38,.08));border-color:rgba(239,68,68,.3);}
.result-icon-right{flex-shrink:0;width:40px;height:40px;background:rgba(255,255,255,.15);border-radius:10px;display:flex;align-items:center;justify-content:center;}
.result-content-right{flex:1;}
.result-label-right{font-size:12px;color:rgba(255,255,255,.7);margin-bottom:4px;}
.result-value-right{font-size:18px;font-weight:700;color:#fff;}

.stats-right{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
.stat-right{padding:12px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:8px;}
.stat-right.confidence{background:rgba(34,197,94,.1);border-color:rgba(34,197,94,.2);}
.stat-right.severity{background:rgba(251,146,60,.1);border-color:rgba(251,146,60,.2);}
.stat-label-right{font-size:11px;color:rgba(255,255,255,.7);margin-bottom:6px;}
.stat-value-right{font-size:16px;font-weight:700;color:#fff;margin-bottom:8px;}
.stat-bar-right{width:100%;height:4px;background:rgba(255,255,255,.1);border-radius:2px;overflow:hidden;}
.stat-fill-right{height:100%;background:linear-gradient(90deg,#22c55e,#16a34a);border-radius:2px;transition:width 0.5s ease;}
.severity-badge-right{padding:4px 8px;background:rgba(251,146,60,.2);border-radius:6px;font-size:12px;text-align:center;color:#fff;}

.treatment-right{padding:16px;background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.2);border-radius:12px;}
.treatment-header-right{display:flex;align-items:center;gap:8px;margin-bottom:12px;color:#22c55e;font-size:14px;font-weight:600;}
.treatment-text-right{font-size:13px;color:rgba(255,255,255,.9);line-height:1.5;}

.other-possibilities-right{margin-top:16px;}
.possibilities-title-right{font-size:14px;font-weight:600;color:#fff;margin-bottom:12px;}
.possibilities-list-right{display:flex;flex-direction:column;gap:8px;}
.possibility-item-right{display:flex;justify-content:space-between;align-items:center;padding:8px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:6px;}
.possibility-name-right{font-size:13px;color:#fff;font-weight:500;}
.possibility-info-right{display:flex;gap:8px;}
.prob-right{font-size:12px;color:#22c55e;font-weight:600;}
.sev-right{font-size:11px;color:rgba(255,255,255,.6);padding:2px 6px;background:rgba(255,255,255,.1);border-radius:4px;}

.external-matches-right{margin-top:16px;}
.matches-title-right{font-size:14px;font-weight:600;color:#fff;margin-bottom:12px;}
.matches-list-right{display:flex;flex-direction:column;gap:8px;}
.match-item-right{display:flex;justify-content:space-between;align-items:center;padding:8px;background:rgba(59,130,246,.05);border:1px solid rgba(59,130,246,.15);border-radius:6px;}
.match-name-right{font-size:12px;color:#60a5fa;font-weight:500;}
.match-id-right{font-size:11px;color:rgba(255,255,255,.5);}

@media (max-width: 1180px){
  .hero{grid-template-columns:1fr;padding:40px 32px 60px;gap:24px;}
  .hero-right{padding:20px 0 0;}
  .stats-bar{grid-template-columns:repeat(2,1fr);}
  .feat-grid{grid-template-columns:1fr;}
  .cat-panel{grid-template-columns:1fr;}
  .cta-card{flex-direction:column;align-items:flex-start;padding:48px 28px;}
  .steps-row{flex-direction:column;gap:16px;}
  .sarr{display:none;}
}

@media (max-width: 760px){
  .nav{padding:12px 14px;gap:8px;}
  .nav-links{display:none;}
  .nav-sub{display:none;}
  .hero-left{padding:26px 0 0;}
  .how-sec,.feat-sec,.dis-sec,.cta-sec{padding:70px 18px;}
  .footer{padding:36px 20px 28px;}
  .illus{width:100%;height:360px;}
  .illus-main{width:240px;height:300px;}
}
`;

const CATEGORIES = [
  {
    id: "respiratoire", label: "Respiratoire",
    bg: "linear-gradient(135deg,#1d4ed8,#0891b2)",
    count: 7,
    icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M4 12h4l2-8 4 16 2-8h4"/></svg>,
    miniIcon: "#dbeafe",
    diseases: [
      { name: "Grippe", sub: "Viral · Saisonnier", col: "#eff6ff" },
      { name: "Bronchite", sub: "Inflammation bronchique", col: "#eff6ff" },
      { name: "Pneumonie", sub: "Infection pulmonaire", col: "#eff6ff" },
      { name: "Asthme", sub: "Obstruction respiratoire", col: "#eff6ff" },
      { name: "Sinusite", sub: "Inflammation des sinus", col: "#eff6ff" },
      { name: "Laryngite", sub: "Inflammation du larynx", col: "#eff6ff" },
      { name: "Rhinopharyngite", sub: "Infection naso-pharyngée", col: "#eff6ff" },
    ]
  },
  {
    id: "orl", label: "ORL",
    bg: "linear-gradient(135deg,#7c3aed,#a855f7)",
    count: 4,
    icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/></svg>,
    miniIcon: "#f3e8ff",
    diseases: [
      { name: "Angine", sub: "Infection pharyngée", col: "#faf5ff" },
      { name: "Otite", sub: "Infection de l'oreille", col: "#faf5ff" },
      { name: "Pharyngite", sub: "Inflammation du pharynx", col: "#faf5ff" },
      { name: "Conjonctivite", sub: "Infection oculaire", col: "#faf5ff" },
    ]
  },
  {
    id: "digestif", label: "Digestif",
    bg: "linear-gradient(135deg,#059669,#10b981)",
    count: 2,
    icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2V9M9 21H5a2 2 0 0 1-2-2V9m0 0h18"/></svg>,
    miniIcon: "#d1fae5",
    diseases: [
      { name: "Gastro-entérite", sub: "Infection gastro-intestinale", col: "#f0fdf4" },
      { name: "Allergie", sub: "Réaction immunitaire", col: "#f0fdf4" },
    ]
  },
  {
    id: "neuro", label: "Neurologique",
    bg: "linear-gradient(135deg,#b45309,#f59e0b)",
    count: 2,
    icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
    miniIcon: "#fef3c7",
    diseases: [
      { name: "Migraine", sub: "Céphalée vasculaire", col: "#fffbeb" },
      { name: "Covid-19", sub: "SARS-CoV-2 · Viral", col: "#fffbeb" },
    ]
  },
  {
    id: "urinaire", label: "Urinaire",
    bg: "linear-gradient(135deg,#e11d48,#f43f5e)",
    count: 1,
    icon: <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>,
    miniIcon: "#ffe4e6",
    diseases: [
      { name: "Cystite", sub: "Infection urinaire", col: "#fff1f2" },
    ]
  },
];

const STATS = [
  { c: "#2563eb", v: "10K+", l: "Patients analysés", icon: <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="1.8"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg> },
  { c: "#0891b2", v: "95%", l: "Précision", icon: <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#0891b2" strokeWidth="1.8"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg> },
  { c: "#059669", v: "24/7", l: "Disponible", icon: <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="1.8"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg> },
  { c: "#7c3aed", v: "100%", l: "Sécurisé", icon: <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="1.8"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg> },
];

const STEPS = [
  { n: "01", t: "Décrivez vos symptômes", s: "En langage naturel" },
  { n: "02", t: "Analyse NLP", s: "Traitement intelligent" },
  { n: "03", t: "Diagnostic IA", s: "Résultats précis" },
  { n: "04", t: "Recommandations", s: "Conseils médicaux" }
];

const FEATURES = [
  { bg: "linear-gradient(135deg,#1d4ed8,#3b82f6)", t: "Analyse Lexicale", d: "Tokenisation intelligente avec détection des symptômes, négations et intensificateurs", icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg> },
  { bg: "linear-gradient(135deg,#047857,#10b981)", t: "Analyse Syntaxique", d: "POS tagging et identification des structures grammaticales complexes", icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg> },
  { bg: "linear-gradient(135deg,#5b21b6,#8b5cf6)", t: "Prédiction IA", d: "Classification précise des maladies avec score de confiance personnalisé", icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg> },
];

const PTS = Array.from({ length: 14 }, (_, i) => ({ l: `${6 + i * 6.5}%`, sz: `${4 + ((i * 3) % 7)}px`, dur: `${9 + i * 1.1}s`, del: `${i * 0.6}s` }));

const NAV_LINKS = [
  { label: "Fonctionnalités", target: "#fonctionnalites" },
  { label: "Maladies", target: "#maladies" },
  { label: "Comment ça marche", target: "#comment" },
];

function DoctorSVG() {
  return (
    <svg width="264" height="344" viewBox="0 0 264 344" fill="none">
      <circle cx="132" cy="172" r="132" fill="url(#bg)" opacity=".35"/>
      <rect x="77" y="188" width="110" height="132" rx="20" fill="#1a3870"/>
      <rect x="82" y="188" width="100" height="122" rx="18" fill="#2a5aad"/>
      <rect x="107" y="188" width="50" height="122" fill="#3b6fcc"/>
      <path d="M107 188 L132 218 L157 188" fill="#162e60" stroke="#4a80dd" strokeWidth="1.5"/>
      <path d="M107 222 Q92 244 97 264 Q102 279 117 279" stroke="#e2e8f0" strokeWidth="3" fill="none" strokeLinecap="round"/>
      <circle cx="117" cy="281" r="7" fill="#94a3b8" stroke="#cbd5e1" strokeWidth="1.5"/>
      <rect x="52" y="200" width="36" height="90" rx="14" fill="#2a5aad"/>
      <ellipse cx="70" cy="295" rx="14" ry="12" fill="#fcd5a8"/>
      <rect x="176" y="200" width="36" height="90" rx="14" fill="#2a5aad"/>
      <ellipse cx="194" cy="295" rx="14" ry="12" fill="#fcd5a8"/>
      <rect x="52" y="242" width="26" height="34" rx="4" fill="#f1f5f9"/>
      <rect x="56" y="248" width="18" height="2.5" rx="1" fill="#94a3b8"/>
      <rect x="56" y="254" width="14" height="2.5" rx="1" fill="#94a3b8"/>
      <rect x="56" y="260" width="16" height="2.5" rx="1" fill="#94a3b8"/>
      <rect x="117" y="158" width="30" height="35" rx="12" fill="#fcd5a8"/>
      <ellipse cx="132" cy="132" rx="46" ry="51" fill="#fcd5a8"/>
      <path d="M86 120 Q89 79 132 76 Q175 79 178 120 Q167 92 132 90 Q97 92 86 120Z" fill="#1a0f0a"/>
      <ellipse cx="115" cy="127" rx="6" ry="7" fill="#fff"/>
      <ellipse cx="149" cy="127" rx="6" ry="7" fill="#fff"/>
      <ellipse cx="116" cy="128" rx="3.5" ry="4" fill="#1a3a6e"/>
      <ellipse cx="150" cy="128" rx="3.5" ry="4" fill="#1a3a6e"/>
      <circle cx="117" cy="127" r="1.2" fill="#fff"/>
      <circle cx="151" cy="127" r="1.2" fill="#fff"/>
      <path d="M109 118 Q115 114 121 118" stroke="#1a0f0a" strokeWidth="2" fill="none" strokeLinecap="round"/>
      <path d="M143 118 Q149 114 155 118" stroke="#1a0f0a" strokeWidth="2" fill="none" strokeLinecap="round"/>
      <path d="M130 135 Q127 144 132 146 Q137 144 134 135" stroke="#e8b890" strokeWidth="1.5" fill="none"/>
      <path d="M121 155 Q132 165 143 155" stroke="#c89060" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
      <rect x="160" y="216" width="20" height="26" rx="4" fill="#dbeafe"/>
      <circle cx="170" cy="223" r="4" fill="#3b82f6"/>
      <rect x="164" y="231" width="12" height="2" rx="1" fill="#93c5fd"/>
      <rect x="166" y="235" width="8" height="2" rx="1" fill="#93c5fd"/>
      <rect x="125" y="238" width="14" height="4" rx="2" fill="#60a5fa"/>
      <rect x="130" y="233" width="4" height="14" rx="2" fill="#60a5fa"/>
      <defs><radialGradient id="bg" cx="50%" cy="50%" r="50%"><stop offset="0%" stopColor="#3b82f6"/><stop offset="100%" stopColor="#060e22"/></radialGradient></defs>
    </svg>
  );
}

function ShifaaAI() {
  const [symptoms, setSymptoms] = useState("");
  const [activeTab, setActiveTab] = useState("respiratoire");
  const [activeNav, setActiveNav] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [apiError, setApiError] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [internalNlp, setInternalNlp] = useState(null);
  const [showDetailedNlp, setShowDetailedNlp] = useState(false);
  const [apiTopDiseases, setApiTopDiseases] = useState([]);

  const scrollTo = (target) => {
    const el = document.querySelector(target);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  useEffect(() => {
    const sections = [
      { id: "fonctionnalites", hash: "#fonctionnalites" },
      { id: "comment", hash: "#comment" },
      { id: "maladies", hash: "#maladies" },
    ];
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          const found = sections.find((s) => s.id === e.target.id);
          if (found) setActiveNav(found.hash);
        }
      });
    }, { threshold: 0.4 });

    sections.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const normalize = (text) => {
    const accents = { e: /[éèêë]/g, a: /[àâä]/g, o: /[ôö]/g, u: /[ùûü]/g, i: /[îï]/g, c: /[ç]/g };
    let out = (text || "").toLowerCase();
    out = out.replace(accents.e, "e").replace(accents.a, "a").replace(accents.o, "o").replace(accents.u, "u").replace(accents.i, "i").replace(accents.c, "c");
    return out;
  };

  const cleanWord = (w) => (w || "").toLowerCase().replace(/[.,;:!?()\[\]{}'\"«»]/g, "");

  const analyzeLexicalLocal = (text) => {
    const symptomsSet = new Set(["fievre", "toux", "gorge", "douleur", "fatigue", "nausee", "vomissement", "diarrhee", "respirer", "respiration", "poitrine", "maux", "tete"]);
    const negations = new Set(["pas", "ne", "non", "jamais", "sans", "aucun", "aucune"]);
    const intensifiers = new Set(["tres", "fort", "forte", "intense", "leger", "legere", "beaucoup"]);
    const timeWords = new Set(["depuis", "hier", "aujourdhui", "pendant", "jours", "semaine", "nuits"]);

    const words = text.split(/\s+/).filter(Boolean);
    const tokens = words.map((word) => {
      const norm = normalize(cleanWord(word));
      let type = "mot";
      if (symptomsSet.has(norm)) type = "symptome";
      else if (negations.has(norm)) type = "negation";
      else if (intensifiers.has(norm)) type = "intensificateur";
      else if (timeWords.has(norm)) type = "temps";
      return { word, norm, type };
    });

    return {
      tokens,
      stats: {
        total: tokens.length,
        symptoms: tokens.filter((t) => t.type === "symptome").length,
        negations: tokens.filter((t) => t.type === "negation").length,
        intensifiers: tokens.filter((t) => t.type === "intensificateur").length,
      },
    };
  };

  const analyzeSyntaxLocal = (tokens) => {
    const verbs = new Set(["ai", "as", "a", "avons", "etes", "suis", "est", "tousse", "respire", "souffre", "vomis"]);
    const det = new Set(["le", "la", "les", "un", "une", "des", "du", "de"]);
    return tokens.map((t) => {
      const w = normalize(cleanWord(t.word));
      let pos = "MOT";
      let role = "terme";
      if (verbs.has(w)) { pos = "VERBE"; role = "action"; }
      else if (det.has(w)) { pos = "DET"; role = "determinant"; }
      else if (t.type === "symptome") { pos = "NOM"; role = "symptome"; }
      else if (t.type === "temps") { pos = "ADV"; role = "temporalite"; }
      return { word: t.word, pos, role };
    });
  };

  const buildTree = (syntaxRows) => {
    if (!syntaxRows.length) return "Aucune structure detectee";
    const chunks = [];
    let current = [];
    syntaxRows.forEach((row, i) => {
      current.push(row.word);
      if (row.pos === "VERBE" || i === syntaxRows.length - 1) {
        chunks.push(`|- ${current.join(" ")}`);
        current = [];
      }
    });
    return `Structure de phrase:\n${chunks.join("\n")}`;
  };

  const analyzeSymptoms = async () => {
    const text = symptoms.trim();
    if (!text) {
      setApiError("Veuillez saisir une description de symptômes avant l'analyse.");
      setAnalysisResult(null);
      setInternalNlp(null);
      setApiTopDiseases([]);
      return;
    }

    const lexical = analyzeLexicalLocal(text);
    const syntax = analyzeSyntaxLocal(lexical.tokens);
    setInternalNlp({ lexical, syntax, tree: buildTree(syntax) });

    try {
      setIsAnalyzing(true);
      setApiError("");

      const apiBaseUrl = (typeof window !== "undefined" && window.__SHIFAAI_API_BASE_URL)
        ? String(window.__SHIFAAI_API_BASE_URL).replace(/\/$/, "")
        : (typeof window !== "undefined" && window.location && window.location.protocol !== "file:")
          ? `${window.location.protocol}//${window.location.hostname}:5000`
          : "http://127.0.0.1:5000";

      const response = await fetch(`${apiBaseUrl}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || `Erreur HTTP ${response.status}`);
      }

      setAnalysisResult(payload);

      const searchQuery = (payload.top_prediction && payload.top_prediction.disease && payload.top_prediction.disease !== "Non déterminé")
        ? payload.top_prediction.disease
        : text;

      let topDiseases = [];
      try {
        const extResp = await fetch(`${apiBaseUrl}/api/external/disease-info`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ disease: searchQuery }),
        });
        const extPayload = await extResp.json();
        if (extResp.ok && extPayload.results) {
          topDiseases = extPayload.results.slice(0, 10);
        }
      } catch (_err) {
        // Fallback silently to already available matches
      }

      if (!topDiseases.length) {
        try {
          const q = encodeURIComponent(searchQuery || "disease");
          const olsResp = await fetch(`https://www.ebi.ac.uk/ols4/api/search?q=${q}&ontology=doid&rows=10`);
          const olsPayload = await olsResp.json();
          const docs = olsPayload?.response?.docs || [];
          topDiseases = docs.slice(0, 10).map((d) => ({
            id: d.obo_id || d.short_form || "N/A",
            label: d.label || "Unknown",
            source: "ols4-doid",
            description: Array.isArray(d.description) ? (d.description[0] || "") : (d.description || ""),
          }));
        } catch (_err) {
          // If OLS fails too, keep fallback below
        }
      }

      if (!topDiseases.length && payload.external_matches) {
        topDiseases = payload.external_matches.slice(0, 10);
      }

      setApiTopDiseases(topDiseases);
    } catch (error) {
      setAnalysisResult(null);
      setApiTopDiseases([]);
      setApiError(error.message || "Erreur inattendue pendant l'analyse.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const cat = CATEGORIES.find((c) => c.id === activeTab);

  return (
    <>
      <style>{css}</style>
      <div className="sr">
        <nav className="nav">
          <div className="nav-brand" onClick={() => scrollTo("#hero")}>
            <div className="nav-logo">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            </div>
            <div>
              <div className="nav-name">ShifaaAI</div>
              <div className="nav-sub">Plateforme d'Analyse Médicale par IA</div>
            </div>
          </div>
          <div className="nav-links">
            {NAV_LINKS.map((l) => (
              <button key={l.label} className={`nav-link${activeNav === l.target ? " active" : ""}`} onClick={() => scrollTo(l.target)}>
                {l.label}
              </button>
            ))}
          </div>
          <button className="nav-cta" onClick={() => scrollTo("#hero")}>Démarrer l'analyse</button>
        </nav>

        <section className="hero" id="hero">
          <div className="particles">
            {PTS.map((p, i) => <div key={i} className="pt" style={{ left: p.l, width: p.sz, height: p.sz, animationDuration: p.dur, animationDelay: p.del }}/>) }
          </div>
          <div className="hero-left">
            <div className="hero-badge"><div className="bdot"/><span className="btxt">IA Médicale · Version 3.0.0</span></div>
            <h1 className="h1">Analysez vos<br/>symptômes avec<br/><span>l'Intelligence Artificielle</span></h1>
            <p className="desc">ShifaaAI utilise le traitement du langage naturel pour analyser vos symptômes et vous fournir un diagnostic précis en quelques secondes.</p>
            <div className="hero-form">
              <label className="f-lbl">Décrivez vos symptômes en langage naturel</label>
              <textarea className="f-ta" placeholder="Ex: J'ai une très forte fièvre depuis 3 jours, des maux de tête intenses et une toux sèche..." value={symptoms} onChange={(e) => setSymptoms(e.target.value)}/>
              <button className="f-btn" onClick={analyzeSymptoms} disabled={isAnalyzing}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                {isAnalyzing ? "Analyse en cours..." : "Analyser mes symptômes"}
              </button>
              {apiError && <div className="api-msg err">{apiError}</div>}
              {internalNlp && (
                <div className="internal-panel">
                  <div className="internal-head">
                    <div className="internal-title">Analyse syntaxique avancée</div>
                    <button className="detail-btn" onClick={() => setShowDetailedNlp((v) => !v)}>
                      {showDetailedNlp ? "Vue simplifiée" : "Vue détaillée"}
                    </button>
                  </div>
                  
                  <div className="analysis-section">
                    <h5 className="section-title">Analyse lexicale</h5>
                    <div className="tok-wrap">
                      {internalNlp.lexical.tokens.slice(0, showDetailedNlp ? internalNlp.lexical.tokens.length : 40).map((t, idx) => (
                        <span
                          key={`${t.word}-${idx}`}
                          className={`tok ${t.type === "SYMPTOM" ? "sym" : t.type === "NEGATION" ? "neg" : t.type === "INTENSIFIER" ? "int" : t.type === "WORD" ? "word" : ""}`}
                          title={`Type: ${t.type} | Index: ${idx}`}
                        >
                          {t.word}
                          <span className="token-type">{t.type}</span>
                        </span>
                      ))}
                    </div>
                    <div className="mini-stats">
                      <div className="mini-stat">
                        <div className="stat-number">{internalNlp.lexical.stats.total}</div>
                        <div className="stat-label">Mots total</div>
                      </div>
                      <div className="mini-stat stat-symptom">
                        <div className="stat-number">{internalNlp.lexical.stats.symptoms}</div>
                        <div className="stat-label">Symptômes</div>
                      </div>
                      <div className="mini-stat stat-negation">
                        <div className="stat-number">{internalNlp.lexical.stats.negations}</div>
                        <div className="stat-label">Négations</div>
                      </div>
                      <div className="mini-stat stat-intensifier">
                        <div className="stat-number">{internalNlp.lexical.stats.intensifiers}</div>
                        <div className="stat-label">Intensificateurs</div>
                      </div>
                    </div>
                  </div>

                  <div className="analysis-section">
                    <h5 className="section-title">Analyse syntaxique</h5>
                    <div className="syntax-info">
                      <p><strong>Structure grammaticale :</strong> Identification des parties du discours et relations syntaxiques</p>
                    </div>
                    <table className="syntax-table">
                      <thead>
                        <tr>
                          <th>Mot</th>
                          <th>Type grammatical</th>
                          <th>Rôle syntaxique</th>
                          <th>Catégorie</th>
                        </tr>
                      </thead>
                      <tbody>
                        {internalNlp.syntax.slice(0, showDetailedNlp ? internalNlp.syntax.length : 15).map((s, i) => (
                          <tr key={`${s.word}-${i}`} className="syntax-row">
                            <td className="word-cell">
                              <strong>{s.word}</strong>
                            </td>
                            <td>
                              <span
                                className={`pos-pill ${
                                  s.pos === "VERBE" ? "pos-verb" :
                                  s.pos === "NOM" ? "pos-nom" :
                                  s.pos === "DET" ? "pos-det" :
                                  s.pos === "ADV" ? "pos-adv" :
                                  s.pos === "ADJ" ? "pos-adj" :
                                  s.pos === "PREP" ? "pos-prep" : "pos-default"
                                }`}
                                title={`Partie du discours: ${s.pos}`}
                              >
                                {s.pos}
                              </span>
                            </td>
                            <td className="role-cell">{s.role || "Non défini"}</td>
                            <td>
                              <span className={`category-tag ${
                                s.pos === "VERBE" ? "tag-verb" :
                                s.pos === "NOM" ? "tag-nom" :
                                s.pos === "DET" ? "tag-det" :
                                s.pos === "ADV" ? "tag-adv" :
                                s.pos === "ADJ" ? "tag-adj" :
                                s.pos === "PREP" ? "tag-prep" : "tag-default"
                              }`}>
                                {s.pos === "VERBE" ? "Action" :
                                 s.pos === "NOM" ? "Entité" :
                                 s.pos === "DET" ? "Déterminant" :
                                 s.pos === "ADV" ? "Modifieur" :
                                 s.pos === "ADJ" ? "Qualificatif" :
                                 s.pos === "PREP" ? "Lien" : "Autre"}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {showDetailedNlp && internalNlp.tree && (
                    <div className="analysis-section">
                      <h5 className="section-title">Arbre syntaxique</h5>
                      <div className="tree-box">
                        <pre>{internalNlp.tree}</pre>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
          <div className="hero-right">
            {analysisResult ? (
              <div className="results-right-panel">
                <div className="results-header-right">
                  <h3 className="results-title-right">Résultats de l'analyse</h3>
                  <p className="results-subtitle-right">Diagnostic IA complet</p>
                </div>
                
                <div className="result-card-right main">
                  <div className="result-icon-right">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
                  </div>
                  <div className="result-content-right">
                    <div className="result-label-right">Maladie prédite</div>
                    <div className="result-value-right">{analysisResult.top_prediction?.disease || "N/A"}</div>
                  </div>
                </div>
                
                <div className="stats-right">
                  <div className="stat-right confidence">
                    <div className="stat-label-right">Confiance</div>
                    <div className="stat-value-right">{analysisResult.top_prediction?.probability || "N/A"}%</div>
                    <div className="stat-bar-right">
                      <div className="stat-fill-right" style={{width: `${analysisResult.top_prediction?.probability || 0}%`}}></div>
                    </div>
                  </div>
                  
                  <div className="stat-right severity">
                    <div className="stat-label-right">Sévérité</div>
                    <div className="stat-value-right severity-badge-right">{analysisResult.top_prediction?.severity || "N/A"}</div>
                  </div>
                </div>
                
                <div className="treatment-right">
                  <div className="treatment-header-right">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="2"><path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z"/></svg>
                    <span>Traitement recommandé</span>
                  </div>
                  <div className="treatment-text-right">{analysisResult.top_prediction?.treatment || "N/A"}</div>
                </div>
                
                {analysisResult.predictions && analysisResult.predictions.length > 1 && (
                  <div className="other-possibilities-right">
                    <h4 className="possibilities-title-right">Autres possibilités</h4>
                    <div className="possibilities-list-right">
                      {analysisResult.predictions.slice(1, 3).map((pred, idx) => (
                        <div key={idx} className="possibility-item-right">
                          <div className="possibility-name-right">{pred.disease}</div>
                          <div className="possibility-info-right">
                            <span className="prob-right">{pred.probability}%</span>
                            <span className="sev-right">{pred.severity}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {analysisResult.external_matches && analysisResult.external_matches.length > 0 && (
                  <div className="external-matches-right">
                    <h4 className="matches-title-right">Correspondances externes</h4>
                    <div className="matches-list-right">
                      {analysisResult.external_matches.slice(0, 2).map((item, idx) => (
                        <div key={idx} className="match-item-right">
                          <div className="match-name-right">{item.label || "Unknown"}</div>
                          <div className="match-id-right">{item.id || "N/A"}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="illus">
                <div className="illus-main">
                  <div className="illus-inner">
                    <div className="illus-glow"/>
                    <DoctorSVG/>
                  </div>
                </div>
                <div className="pill pill-1">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.2"><polyline points="20 6 9 17 4 12"/></svg>
                  <div><div className="pill-name">Diagnostic précis</div><div className="pill-info">95% de précision</div></div>
                </div>
                <div className="pill pill-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" strokeWidth="2.2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                  <div><div className="pill-name">Résultat rapide</div><div className="pill-info">En quelques secondes</div></div>
                </div>
                <div className="pill pill-3">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#c084fc" strokeWidth="2.2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                  <div><div className="pill-name">100% Sécurisé</div><div className="pill-info">Données protégées</div></div>
                </div>
              </div>
            )}
          </div>
        </section>

        <section className="how-sec" id="comment">
          <div className="sec-hdr">
            <h2 className="sec-ttl">Comment ça marche ?</h2>
            <p className="sec-sub">Un processus simple et rapide en 4 étapes</p>
          </div>
          <div className="steps-row">
            {STEPS.map((s, i) => (
              <div key={s.n} style={{ display: "contents" }}>
                <div className="step-card"><div className="sn">{s.n}</div><div className="st">{s.t}</div><div className="ss">{s.s}</div></div>
                {i < STEPS.length - 1 && <div className="sarr">→</div>}
              </div>
            ))}
          </div>
        </section>

        <section className="feat-sec" id="fonctionnalites">
          <div className="sec-hdr">
            <h2 className="sec-ttl-dk">Fonctionnalités <span className="blu">Avancées</span></h2>
            <p className="sec-sub-dk">Une analyse médicale complète en trois étapes</p>
          </div>
          <div className="feat-grid">
            {FEATURES.map((f) => (
              <div key={f.t} className="feat-card">
                <div className="fi" style={{ background: f.bg }}>{f.icon}</div>
                <div className="ft">{f.t}</div>
                <div className="fd">{f.d}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="dis-sec" id="maladies">
          <div className="sec-hdr">
            <h2 className="sec-ttl-dk">Explorer par <span className="blu">Système Médical</span></h2>
            <p className="sec-sub-dk">Naviguez les conditions détectables par catégorie anatomique</p>
          </div>
          <div className="body-explorer">
            {apiTopDiseases.length > 0 && (
              <div className="api-top10">
                <h3>Top 10 maladies détectées réellement via API</h3>
                <p>Résultats récupérés depuis Disease Ontology en fonction de votre analyse.</p>
                <div className="api-grid">
                  {apiTopDiseases.map((d, idx) => (
                    <div className="api-card" key={`${d.id || d.label}-${idx}`}>
                      <h4>{idx + 1}. {d.label || "Unknown"}</h4>
                      <small>ID: {d.id || "N/A"} • Source: {d.source || "API"}</small>
                      <span>{(d.description || "Pas de description.").slice(0, 150)}...</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <div className="body-tabs">
              {CATEGORIES.map((c) => (
                <button key={c.id} className={`body-tab${activeTab === c.id ? " sel" : ""}`} onClick={() => setActiveTab(c.id)}>
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={activeTab === c.id ? "white" : "#64748b"} strokeWidth="2.2">
                    <circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/>
                  </svg>
                  {c.label}
                  <span style={{ background: activeTab === c.id ? "rgba(255,255,255,.25)" : "#e2e8f0", color: activeTab === c.id ? "#fff" : "#64748b", fontSize: 11, fontWeight: 700, padding: "2px 8px", borderRadius: 50 }}>{c.count}</span>
                </button>
              ))}
            </div>

            {cat && (
              <div className="cat-panel">
                <div className="cat-left">
                  <div className="cat-big-card" style={{ background: cat.bg }}>
                    <div>
                      <div className="cat-icon-big">{cat.icon}</div>
                      <div className="cat-name">Système {cat.label}</div>
                      <div className="cat-count">{cat.count} condition{cat.count > 1 ? "s" : ""} détectable{cat.count > 1 ? "s" : ""}</div>
                    </div>
                    <div className="cat-bar"/>
                  </div>
                  <div className="dis-counter">
                    <div className="dis-counter-num">16</div>
                    <div className="dis-counter-lbl">conditions médicales au total détectables par ShifaaAI</div>
                  </div>
                </div>
                <div className="cat-right">
                  {cat.diseases.map((d, i) => (
                    <div key={d.name} className="dis-mini-card" style={{ animationDelay: `${i * 0.05}s` }}>
                      <div className="dis-mini-icon" style={{ background: cat.miniIcon }}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="2.2"><polyline points="20 6 9 17 4 12"/></svg>
                      </div>
                      <div>
                        <div className="dis-mini-name">{d.name}</div>
                        <div className="dis-mini-sub">{d.sub}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>

        <section className="cta-sec">
          <div className="cta-card">
            <div className="ct">
              <div className="ctt">Prêt à commencer ?</div>
              <div className="cts">Analysez vos symptômes maintenant et obtenez des résultats en quelques secondes</div>
            </div>
            <button className="ctabtn" onClick={() => scrollTo("#hero")}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1d4ed8" strokeWidth="2.2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
              Démarrer l'analyse
            </button>
          </div>
        </section>

        <footer className="footer">
          <div className="fbrand">
            <div className="flogo"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
            <span className="fname">ShifaaAI</span>
          </div>
          <p className="ftag">Plateforme d'Analyse Médicale par Intelligence Artificielle</p>
          <div className="fdiv"/>
          <p className="fcpy">© 2026 ShifaaAI. Tous droits réservés. | Version 3.0.0</p>
        </footer>
      </div>
    </>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<ShifaaAI />);
