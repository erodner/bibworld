function abstractclick(element)
{
    abox = document.getElementById(element);
    
    if (abox.style['display'] == "none")
    {
        document.getElementById(element).style['display'] = "inline";
    } else {
        document.getElementById(element).style['display'] = "none";
    }
}
