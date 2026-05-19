
def human_readable_size(size: int) -> str:
    
    try:
        s = float(size)
    except (ValueError, TypeError):
        return "0 B"
        
    for unit in ['B', 'KB', 'MB', 'GB']:
        if s < 1024.0:
            return f"{s:.2f} {unit}"
        s /= 1024.0
    return f"{s:.2f} TB"
