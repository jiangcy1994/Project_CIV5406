def _all_path(CurrentPoint, EndPoint, Store, *, LinkGen, PreviousPath=[], RemainDepth=1):
    if CurrentPoint == EndPoint:
        Store.append(PreviousPath)
    elif RemainDepth > 0:
        for link, en in LinkGen(CurrentPoint):
            if en not in PreviousPath[::2]:
                _all_path(en, EndPoint, Store, LinkGen=LinkGen, PreviousPath=PreviousPath+[link,en], RemainDepth=RemainDepth-1)

def all_path(CurrentPoint, EndPoint, *, LinkGen, MininumPath=10, LargestDepth=24):
    for i in range(1, LargestDepth+1):
        store = []
        _all_path(CurrentPoint, EndPoint, store ,LinkGen=LinkGen, PreviousPath=[CurrentPoint], RemainDepth=i)
        if len(store) >= MininumPath:
            break
    return store
