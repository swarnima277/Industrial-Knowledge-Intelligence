import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
export default function Dashboard(){
return <div style={{display:'flex'}}>
<Sidebar/>
<div style={{flex:1}}>
<Navbar/>
<div style={{padding:20}}>
<h1>Dashboard</h1>
<div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:16}}>
{['Documents','Compliance','AI Queries','Progress'].map((t,i)=><div key={i} style={{background:'#e2e8f0',padding:20,borderRadius:10}}><h3>{t}</h3><h2>{[1250,96,342,'72%'][i]}</h2></div>)}
</div>
</div>
</div></div>}