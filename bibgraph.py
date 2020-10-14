import json

""" build json file for treemap """
def getGraphJSON(refs):
    # create nodes
    nodes = {}
    nodes["root"] = {'children': [], 'name': 'publications'}
    children = {}
    for k in refs:
        if 'parent' in refs[k]:
            n = {}
            n['children'] = []
            n['id'] = k
            n['data'] = {}
            if 'year' in refs[k]:
                n['data']['$area'] = 300
                n['data']['leaf'] = True
#/ (2015 - int(refs[k]['year']))
            else:
                n['data']['$area'] = 300
                n['data']['leaf'] = False

            n = dict(n.items() + refs[k].items())

            p = refs[k]['parent'] 
            
            if not p in children:
                children[p] = []
            children[p].append(k)

            nodes[k] = n
            
    def buildtree( nodes, children, nodekey="root" ):
        t = nodes[nodekey]

        # check whether the node has any children
        if nodekey in children:
            areasum = 0
            for k in children[nodekey]:
                c = buildtree( nodes, children, k ) 
                if not c is None:
                    areasum = areasum + c['data']['$area']
                    t['children'].append (c)

            if not 'data' in t:
                t['data'] = {}
            t['data']['$area'] = areasum
        elif not t['data']['leaf']:
            return None

        return t

    tree = buildtree( nodes, children )
    #with open('graph.json', 'w') as f:
    #    json.dump( tree, f, indent=4 )
    return json.dumps( tree, indent=4 )

             
