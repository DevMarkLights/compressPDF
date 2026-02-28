import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [sizeBeforeCompression, setSizeBeforeCompression] = useState('')
  const [sizeAfterCompression, setSizeAfterCompression] = useState('')
  const [isLoading,setIsLoading] = useState(false)
  function addFiles(files){
    
  }

  async function upload(file){
    setIsLoading(true)
    var quality = document.getElementById('quality').value

    const formData = new FormData();
    formData.append('file', file[0])
    formData.append('quality',quality)

    var location = window.location.href

    const response = await fetch(`${location}compress`, {
      method: "POST",
      body: formData,
    });

    fetch(`${location}removeFiles`,{method:"GET"})

    var original_file_size = response.headers.get('X-File-Size-MB')
    setSizeBeforeCompression(original_file_size)
    var compressed_file_size = response.headers.get('X-File-Size-Compressed-MB')
    setSizeAfterCompression(compressed_file_size)

    var filename = file[0].name.replace('.pdf','_compressed.pdf')

    const blob = await response.blob();

    if(blob != null && blob != undefined){
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setIsLoading(false)
      return
    }
    setIsLoading(false)

    
  }

  return (
    <>
      <div>
        <h1>Compress PDF</h1>
        <p>Quality</p>
        <select id='quality' >
          <option value='screen'>Low</option>
          <option value='ebook'>Medium</option>
          <option value='printer'>High</option>
          <option value='prepress'>Very High</option>
        </select>
        <p style={{color:'red'}}>ONLY ACCEPTS PDFs less than 50 Mbs</p>
        <p>File will automatically be downloaded</p>
        <div className='fileDropDiv'>
          <input
              id='fileDrop'
              type="file"
              single='true'
              onChange={e => upload([...e.target.files])}
            />
          <p>file zize before compression: {sizeBeforeCompression}</p>
          <p>file zize after compression: {sizeAfterCompression}</p>
          {/* <button style={{margin: '20px 0'}} onClick={() => upload()}>Upload</button> */}
        </div>
        {isLoading &&
          <div className='loadingContainer'>
            <div className='loader'></div>
          </div>
        } 
      </div>
    </>
  )
}

export default App
