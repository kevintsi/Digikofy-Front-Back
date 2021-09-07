import React, { useEffect, useState } from "react"
import Coffee from "../Coffee/Coffee"

export default function Home() {
    
    const [coffees, setCoffees] = useState([])

    const getCoffees = async () => {
        try {
            const res = await fetch("http://localhost:8000/coffees",{ method : "GET"})

            const data = await res.json()

            console.log("Result : ", data)

            setCoffees(data)
                
        } catch (error) {
            console.log("Something went wrong => ", error)
        }
    }
    
    useEffect(() => {
        getCoffees()
    }, [])

    return (
        <div>
            <div>Home</div>
            <div>List of coffees</div>
            {coffees.map((coffee) => (<Coffee key={coffee.id} coffee={coffee} />))}
        </div>
    )
}