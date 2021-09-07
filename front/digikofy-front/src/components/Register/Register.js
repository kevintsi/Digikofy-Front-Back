import React, { useState } from "react"

export default function Register() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    
    return (
        <div>
            <div>Login</div>
            <div>
                <label>Email : </label>
                <input placeholder="Input your email here" type="email" value={email} onChange={(e) => {setEmail(e.target.value)}}/>
                <label>Password : </label>
                <input placeholder="Input your password here" type="password" value={password} onChange={(e) => {setPassword(e.target.value)}}/>
                <button>OK</button>
            </div>
        </div>
    )
}