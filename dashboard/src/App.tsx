import {useCallback,useEffect,useMemo,useState} from "react";
type Host={host_id:string;hostname:string;ip:string|null;last_seen:string;status:string;risk_score:number;risk_level:string;quarantine_state:string};
type EventItem={id:number;host_id:string;hostname:string;timestamp:string;rule:string;severity:string;risk_score:number;detail:Record<string,unknown>};
async function api(path:string,key:string,init:RequestInit={}){
 const response=await fetch(path,{...init,headers:{"Content-Type":"application/json","X-Admin-Key":key,...(init.headers||{})}});
 if(!response.ok){const body=await response.json().catch(()=>({}));throw new Error(body.detail||"Request failed: "+response.status);}
 return response.json();
}
function ago(value:string){const sec=Math.max(0,Math.floor((Date.now()-new Date(value).getTime())/1000));return sec<60?sec+"s ago":sec<3600?Math.floor(sec/60)+"m ago":Math.floor(sec/3600)+"h ago";}
export default function App(){
 const [key,setKey]=useState(localStorage.getItem("sekat_admin_key")||"");
 const [draft,setDraft]=useState(key),[connected,setConnected]=useState(false);
 const [hosts,setHosts]=useState<Host[]>([]),[events,setEvents]=useState<EventItem[]>([]);
 const [error,setError]=useState(""),[busy,setBusy]=useState(""),[filter,setFilter]=useState("all");
 const refresh=useCallback(async()=>{if(!key)return;try{const [h,e]=await Promise.all([api("/api/hosts",key),api("/api/events?limit=80",key)]);setHosts(h.hosts);setEvents(e.events);setConnected(true);setError("");}catch(err){setConnected(false);setError(err instanceof Error?err.message:"API connection failed");}},[key]);
 useEffect(()=>{refresh();const timer=window.setInterval(refresh,5000);return()=>window.clearInterval(timer);},[refresh]);
 const stats=useMemo(()=>({total:hosts.length,online:hosts.filter(h=>h.status==="online").length,warn:hosts.filter(h=>h.risk_score>=40&&h.risk_score<70).length,critical:hosts.filter(h=>h.risk_score>=70).length}),[hosts]);
 const visible=filter==="all"?events:events.filter(e=>e.rule===filter);
 async function command(host:Host,action:"isolate"|"release"){
  if(!window.confirm(action==="isolate"?"Queue SIMULATED isolation? Network remains unchanged.":"Queue simulated release?"))return;
  setBusy(host.host_id);
  try{await api("/api/hosts/"+encodeURIComponent(host.host_id)+"/commands",key,{method:"POST",body:JSON.stringify({action})});await refresh();}
  catch(err){setError(err instanceof Error?err.message:"Command failed");}finally{setBusy("");}
 }
 return <div className="shell">
  <aside className="sidebar"><div className="brand"><b>S</b><div><strong>SEKAT</strong><small>DEFENSE CONSOLE</small></div></div><p className="side-label">WORKSPACE</p><div className="nav active">◈ &nbsp; Overview</div><div className="nav">⌁ &nbsp; Endpoints</div><div className="nav">◎ &nbsp; Event stream</div><div className="side-foot">● &nbsp; LAB MODE <small>v1.0</small></div></aside>
  <main className="main"><header><div><p className="eyebrow">SECURITY OPERATIONS / OVERVIEW</p><h1>Endpoint overview</h1></div><div className="head-actions"><span className={connected?"connected":"disconnected"}>● {connected?"API connected":"Disconnected"}</span>{key&&<button className="ghost" onClick={()=>{localStorage.removeItem("sekat_admin_key");setKey("");setDraft("");setConnected(false);}}>Lock console</button>}</div></header>
  {!key?<section className="login panel"><p className="eyebrow">AUTHENTICATED ACCESS</p><h2>Connect to your SEKAT lab</h2><p>Masukkan admin API key dari file .env. Key disimpan di localStorage browser ini.</p><form onSubmit={e=>{e.preventDefault();const k=draft.trim();if(k){localStorage.setItem("sekat_admin_key",k);setKey(k);}}}><input type="password" value={draft} onChange={e=>setDraft(e.target.value)} placeholder="SEKAT_ADMIN_API_KEY"/><button className="primary">Connect dashboard</button></form></section>:<>
   {error&&<div className="error">{error}</div>}
   <section className="stats"><div className="stat"><small>REGISTERED ENDPOINTS</small><strong>{stats.total.toString().padStart(2,"0")}</strong><em>All known hosts</em></div><div className="stat"><small>ONLINE NOW</small><strong>{stats.online.toString().padStart(2,"0")}</strong><em>Heartbeat within 30s</em></div><div className="stat warn"><small>NEEDS ATTENTION</small><strong>{stats.warn.toString().padStart(2,"0")}</strong><em>Risk score 40-69</em></div><div className="stat danger"><small>CRITICAL RISK</small><strong>{stats.critical.toString().padStart(2,"0")}</strong><em>Risk score 70-100</em></div></section>
   <section className="columns"><div className="panel"><div className="panel-head"><div><p className="eyebrow">FLEET MANAGEMENT</p><h2>Monitored endpoints</h2></div><span className="chip">{hosts.length} HOSTS</span></div>
    {!hosts.length?<div className="empty"><b>No endpoints yet</b><p>Run agent or send synthetic telemetry from simulator.</p></div>:hosts.map(h=><article className="host" key={h.host_id}><div className="host-icon">⌘</div><div className="host-name"><b>{h.hostname}</b><small>{h.host_id} · {h.ip||"IP unknown"}</small></div><div className="risk"><div><span className={"badge "+h.risk_level.toLowerCase()}>{h.risk_level}</span><b>{h.risk_score}/100</b></div><i><span style={{width:h.risk_score+"%"}}/></i></div><div className="state"><b className={h.status==="online"?"dot":"dot off"}/> {h.status}<small>{h.quarantine_state.replaceAll("_"," ")}</small></div><button className="action" disabled={busy===h.host_id} onClick={()=>command(h,h.quarantine_state==="isolated_simulated"||h.quarantine_state==="pending"?"release":"isolate")}>{h.quarantine_state==="isolated_simulated"||h.quarantine_state==="pending"?"Release":"Isolate"}</button></article>)}
    <div className="footnote">Containment is simulated only. Endpoint network rules are never modified.</div></div>
    <div className="panel"><p className="eyebrow">DETECTION ENGINE</p><h2>Detection rules</h2>{[["R1","Internal peer spread","3+ private IPv4 peers / 20 sec","+40"],["R2","File activity burst","30+ file events / 10 sec","+35"],["R3","Canary interaction","Configured canary touched","+60"],["R4","Audit finding","Operator-submitted finding","+15"]].map(r=><div className="rule" key={r[0]}><b>{r[0]}</b><div><strong>{r[1]}</strong><small>{r[2]}</small></div><em>{r[3]}</em></div>)}<div className="notice">Scores decay by 10 every 30 seconds for R1-R3. R4 persists.</div></div>
   </section>
   <section className="panel events"><div className="panel-head"><div><p className="eyebrow">LIVE TELEMETRY</p><h2>Recent security events</h2></div><select value={filter} onChange={e=>setFilter(e.target.value)}><option value="all">All rules</option>{["HEARTBEAT","R1","R2","R3","R4"].map(x=><option key={x}>{x}</option>)}</select></div>
    {!visible.length?<div className="empty">No events received.</div>:<div className="table-wrap"><table><thead><tr><th>RULE</th><th>ENDPOINT</th><th>SEVERITY</th><th>RISK</th><th>TIME</th><th>DETAIL</th></tr></thead><tbody>{visible.map(e=><tr key={e.id}><td><span className="tag">{e.rule}</span></td><td><b>{e.hostname}</b><small>{e.host_id}</small></td><td>{e.severity}</td><td>{e.risk_score}</td><td>{ago(e.timestamp)}</td><td className="detail">{JSON.stringify(e.detail)}</td></tr>)}</tbody></table></div>}
    <div className="footnote">Auto-refresh every 5 seconds · latest 80 events</div></section>
  </>}
  <footer>SEKAT · DEFENSIVE LAB PROTOTYPE <span>SYNTHETIC TELEMETRY · SIMULATED CONTAINMENT</span></footer></main></div>;
}
