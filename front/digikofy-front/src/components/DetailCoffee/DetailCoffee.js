import React, { useEffect, useState } from "react"
import { useParams } from "react-router"

export default function DetailCoffee() {
    let {id} = useParams()

    const [coffee, setCoffee] = useState({})

    const getCoffee = async (id) => {

        try {
            const res = await fetch(`https://digikofy-front-back.herokuapp.com/api/coffee/${id}`,{ method : "GET"})

            const data = await res.json()

            console.log("Result : ", data)

            setCoffee(data)
                
        } catch (error) {
            console.log("Something went wrong => ", error)
        }
    }

    useEffect(() => {
        getCoffee(id)
    }, [id])

    return (
        <div>
            <label>{coffee.name}</label><br/>
            <i>{coffee.description}</i>
        </div>
    )
}