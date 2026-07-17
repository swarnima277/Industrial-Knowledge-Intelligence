import {useNavigate} from 'react-router-dom';
export default function Login(){
const nav=useNavigate();
return <div style={{display:'flex',height:'100vh',justifyContent:'center',alignItems:'center',background:'#0f172a',color:'white'}}>
<div style={{background:'#1e293b',padding:30,borderRadius:12,width:320}}>
<h2>EPC AI Platform</h2>
<input placeholder='Email' style={{width:'100%',margin:'8px 0',padding:10}}/>
<input type='password' placeholder='Password' style={{width:'100%',margin:'8px 0',padding:10}}/>
<button style={{width:'100%',padding:10}} onClick={()=>nav('/dashboard')}>Login</button>
</div></div>}