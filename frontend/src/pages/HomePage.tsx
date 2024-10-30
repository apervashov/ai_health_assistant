import { CgGym } from "react-icons/cg";
import { FaBed } from "react-icons/fa6";
import { MdFastfood } from "react-icons/md";
import { useState } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";

import { useLazySendChatQuestionQuery } from "../store/api/chatApi";

const HomePage = () => {

    const [sendChatQuestion, { isLoading,isFetching }] = useLazySendChatQuestionQuery()

    type Category = 'sport' | 'feed' | 'sleep'

    const [category, setCategory] = useState<Category | null>(null)
    const [message, setMessage] = useState<string>('')

    const [context, setContext] = useState<string | null>(null)
    const [sources, setSources] = useState<string[]>([])

    const [chatHistory, setChatHistory] = useState<{ sender: string; text: string }[]>([]);

    async function onSubmit() {
        if (!message.trim()) return;
        setChatHistory([...chatHistory, { sender: 'User', text: message }]);
        setMessage('')
        const question = {
            context: context,
            sources: sources,
            message: message
        }
        try {
            const res = await sendChatQuestion(question).unwrap()
            console.log(res)
            setContext(res.context);
            setSources(res.sources);
            setChatHistory(prev => [...prev, { sender: 'Assistant', text: res.response }]);
        } catch (_) {
            setChatHistory(prev => [...prev, { sender: 'Assistant', text: "Something went wrong" }]);
        }
    }

    useGSAP(()=>{
        gsap.from('#firstheading',{opacity:0.3,ease:'power2.inOut',duration:0.5})
        gsap.from('#secondheading',{opacity:0,y:5,ease:'power2.inOut',delay:0.3,duration:0.5})
        gsap.from('#buttons',{opacity:0,y:5,ease:'power2.inOut',delay:0.3,duration:0.5})
        gsap.from('#input',{opacity:0,y:5,ease:'power2.inOut',duration:0.5})
    },[])

    return (
        <div className='w-full h-full flex flex-col justify-end items-center p-4 gap-8'>
            <div className="w-full overflow-y-auto no-scrollbar h-full  p-2  border-gray-200 mb-4  ">
                {chatHistory.length > 0 ? <>{chatHistory.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex ${msg.sender === 'User' ? 'justify-end' : 'justify-start'} mb-2`}
                    >
                        <div
                            className={`p-2 rounded-lg max-w-xs ${msg.sender === 'User' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'
                                }`}
                        >
                            <p>{msg.text}</p>
                        </div>
                    </div>
                ))}
                    { (isLoading||isFetching) && <div
                        className={`flex justify-start mb-2`}
                    >
                        <div
                            className={`p-2 rounded-lg max-w-xs  bg-gray-200 text-gray-800`}
                        >
                            <p className="flex items-center">I'm thinking  <div className="loader"></div>  </p>
                        </div>
                    </div>}
                </> :
                    <div className="w-full h-full items-center  flex  flex-col gap-2 justify-center">
                        <h1 className="text-xl" id="firstheading" >Ask any question or advice about your health or trainings and let's see what happens</h1>
                        <h2 className="text-gray-600" id="secondheading">Choose a category for a better experience and make your life better with Health AI</h2>
                    </div>
                }
            </div>

            <div id="buttons">
                <div className="flex gap-6">
                    <button onClick={() => setCategory('sport')} className={`flex items-center shadow-lg justify-center gap-2 ${category === 'sport' ? 'bg-bright-blue' : 'bg-gray-300'}  text-white rounded-md font-medium hover:opacity-90 duration-200 h-12 w-40`}>
                        Training <CgGym size={30} />
                    </button>
                    <button onClick={() => setCategory('sleep')} className={`flex items-center shadow-lg justify-center gap-2  ${category === 'sleep' ? 'bg-bright-blue' : 'bg-gray-300'} text-white rounded-md font-medium hover:opacity-90 duration-200 h-12 w-40`}>
                        Sleep  <FaBed size={25} />
                    </button>
                    <button onClick={() => setCategory('feed')} className={`flex items-center shadow-lg justify-center gap-2  ${category === 'feed' ? 'bg-bright-blue' : 'bg-gray-300'} text-white rounded-md font-medium hover:opacity-90 duration-200 h-12 w-40`}>
                        Feed  <MdFastfood size={20} />
                    </button>
                </div>
            </div>


            <div id="input" className="w-2/3  rounded-xl drop-shadow-2xl mb-20">
                <div className="flex">
                    <input placeholder="Waiting for your question..." value={message} onChange={(e) => setMessage(e.target.value)} className=" w-full px-5 py-2 rounded-l-xl outline-none" type="text" />
                    <button disabled={isLoading||isFetching} onClick={onSubmit} className="bg-black rounded-r-xl px-4 py-2 text-white font-semibold hover:bg-slate-700">Send</button>
                </div>
            </div>
        </div>
    )
}

export default HomePage;
