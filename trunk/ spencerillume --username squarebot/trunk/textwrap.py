
def truncline(text, font, maxwidth):
        real=len(text)       
        stext=text           
        l=font.size(text)[0]
        cut=0
        a=0                  
        done=1
        old = None
        while l > maxwidth:
            a=a+1
            n=text.rsplit(None, a)[0]
            if stext == n:
                cut += 1
                stext= n[:-cut]
            else:
                stext = n
            l=font.size(stext)[0]
            real=len(stext)               
            done=0                        
        return real, done, stext             
        
def wrapline(text, font, maxwidth): 
    done=0                      
    wrapped=[]                  
                               
    while not done:             
        nl, done, stext=truncline(text, font, maxwidth) 
        wrapped.append(stext.strip())                  
        text=text[nl:]                                 
    return wrapped


def wrap_multi_line(text, font, maxwidth):
    """ returns text taking new lines into account.
    """

    # separate the text into new lines.
    if "\r\n" in text:
        new_line_char = "\r\n"
    elif "\n" in text:
        new_line_char = "\n"
    elif "\r" in text:
        new_line_char = "\r"
    else:
        new_line_char = ""

    if new_line_char:
        lines = text.split(new_line_char)
    else:
        lines = [text]

    return_lines = []
    for text in lines:
        return_lines.extend( wrapline(text, font, maxwidth) )

    return return_lines
