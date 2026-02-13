def _classify_domain(self, patent: Dict) -> str:
    """Classify patent into technology domain based on title/abstract."""
    title = patent.get("patent_title", "")
    abstract = patent.get("patent_abstract", "")
    text = (title + " " + abstract).lower()
    
    # Simple keyword classification
    if any(kw in text for kw in ["battery", "lithium", "cell", "energy storage"]):
        return "battery"
    elif any(kw in text for kw in ["solar", "photovoltaic", "pv"]):
        return "solar"
    elif any(kw in text for kw in ["wind", "turbine"]):
        return "wind"
    elif any(kw in text for kw in ["hydrogen", "fuel cell", "electrolysis"]):
        return "hydrogen"
    elif any(kw in text for kw in ["nuclear", "reactor", "uranium"]):
        return "nuclear"
    elif any(kw in text for kw in ["cooling", "thermal", "heat"]):
        return "cooling"
    else:
        return "energy"
