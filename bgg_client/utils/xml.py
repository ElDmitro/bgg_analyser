def find_tags_by_attr(xml_tree, tag, attr_key, attr_value):
    return [
        cand for cand in xml_tree.findall(tag)
        if cand.get(attr_key) == attr_value
    ]

def find_tag_by_attr(xml_tree, tag, attr_key, attr_value):
    return find_tags_by_attr(xml_tree, tag, attr_key, attr_value).pop()
