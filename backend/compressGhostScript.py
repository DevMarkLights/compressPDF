import subprocess
import sys
import os
import logging

logger = logging.getLogger(__name__)

def find_ghostscript():
    """Find Ghostscript executable on Windows"""
    # Exact paths based on your installation
    possible_paths = [
        r"C:\Program Files\gs\gs10.06.0\bin\gswin64c.exe",  
        r"C:\Program Files\gs\gs10.06.0\bin\gswin64.exe",   
        "gswin64c",  
        "gswin64",   
        "gs",        
    ]
    
    for gs_path in possible_paths:
        try:
            logger.info(f"Testing Ghostscript at: {gs_path}")
            
            # Check if file exists
            if gs_path.startswith("C:") and not os.path.exists(gs_path):
                logger.info(f"File does not exist: {gs_path}")
                continue
                
            # Test if executable works
            result = subprocess.run([gs_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"Found working Ghostscript at: {gs_path}")
                return gs_path
        except Exception as e:
            logger.info(f"Failed to run {gs_path}: {e}")
            continue
    
    return None

def compress_pdf(input_path, output_path, quality="screen"):
    """
    Compress PDF using Ghostscript with optimized settings
    """
    
    # Validate inputs
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Get file size for timeout estimation
    input_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    logger.info(f"Input file size: {input_size_mb:.2f} MB")
    
    # Dynamic timeout based on file size
    timeout_seconds = max(120, int(input_size_mb * 30))
    logger.info(f"Setting timeout to: {timeout_seconds} seconds")
    
    # Find Ghostscript executable
    gs_executable = find_ghostscript()
    if not gs_executable:
        raise RuntimeError("Ghostscript executable not found")
    
    # Validate quality
    valid_qualities = ['screen', 'ebook', 'printer', 'prepress']
    if quality not in valid_qualities:
        raise ValueError(f"Invalid quality '{quality}'. Must be one of: {valid_qualities}")
    
    # Convert paths to absolute paths
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)
    
    # Ghostscript command with optimized settings for better compression and compatibility
    command = [
        gs_executable,
        "-sDEVICE=pdfwrite",
        f"-dPDFSETTINGS=/{quality}",
        "-dNOPAUSE",
        "-dBATCH",
        "-dSAFER",
        "-dQUIET",
        "-dCompatibilityLevel=1.4",
        "-dPDFX=false",  
        "-dAutoRotatePages=/None",
        "-dCompressFonts=true",
        "-dSubsetFonts=true",
        "-dColorImageDownsampleType=/Bicubic",
        "-dGrayImageDownsampleType=/Bicubic",
        "-dMonoImageDownsampleType=/Bicubic",
        f"-sOutputFile={output_path}",
        input_path,
    ]
    
    logger.info(f"Running Ghostscript with {timeout_seconds}s timeout")
    logger.info(f"Command: {' '.join(command[:8])}... [truncated]")
    
    try:
        # Run with dynamic timeout
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout_seconds
        )
        
        logger.info("Ghostscript compression completed successfully")
        
        # Verify output file was created and has content
        if not os.path.exists(output_path):
            raise RuntimeError("Output file was not created")
        
        output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        compression_ratio = (1 - output_size_mb / input_size_mb) * 100
        
        logger.info(f"Compression successful:")
        logger.info(f"  Original: {input_size_mb:.2f} MB")
        logger.info(f"  Compressed: {output_size_mb:.2f} MB")
        logger.info(f"  Reduction: {compression_ratio:.1f}%")
            
    except subprocess.TimeoutExpired:
        logger.error(f"Ghostscript timed out after {timeout_seconds} seconds")
        # Clean up partial file
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass
        raise RuntimeError(f"PDF compression timed out after {timeout_seconds//60} minutes. File may be too complex or corrupted.")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Ghostscript failed with return code {e.returncode}")
        logger.error(f"Ghostscript error: {e.stderr}")
        
        # Ghostscript error messages
        error_msg = e.stderr.lower() if e.stderr else ""
        if "invalidfont" in error_msg:
            raise RuntimeError("PDF contains invalid fonts. Try a different quality setting.")
        elif "stackoverflow" in error_msg:
            raise RuntimeError("PDF structure is too complex. Try with 'printer' or 'prepress' quality.")
        elif "syntaxerror" in error_msg:
            raise RuntimeError("PDF file appears to be corrupted or invalid.")
        else:
            raise RuntimeError(f"PDF compression failed: {e.stderr or 'Unknown Ghostscript error'}")
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise RuntimeError(f"Unexpected error during compression: {str(e)}")