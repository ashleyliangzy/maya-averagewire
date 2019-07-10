import maya.api.OpenMaya as om
import pymel.core as pm
import pymel.core.datatypes as dt

connected_edge_list=[]#暂存一下连通的边，最后都要统一存到dictionary里
sort_connected_edge_list=[]
connected_vtx_list=[]

g_sel_edge_list=[]
g_sel_edge_list_temp=[]
g_connected_edge_dic=dict()#存所有的连通边的组
g_sort_vtx_dic=dict()#存所有排好序的顶点
g_conected_edge_index=1

#循环vtx所连接的边，找出其中被选择的边
def get_connected_edge_inlist(vtx,edge_list,cur_edge):
    if vtx in connected_vtx_list:
        return False 
    for e in edge_list:
        isconnected=vtx.isConnectedTo(e)
        if isconnected and (e!=cur_edge):
            return e
    return False 
         
def get_connected_edge(input_edge,sel_edge_list):
    evlist=input_edge.connectedVertices()#得到边的两个顶点
    for ev in evlist:
        ce=get_connected_edge_inlist(ev,sel_edge_list,input_edge)
        if ce!=False:
            connected_vtx_list.append(ev)#已经找过的顶点存起来，以免重复计算
            connected_edge_list.append(ce)
            #g_sel_edge_list_temp.remove(ce)      
            get_connected_edge(ce,sel_edge_list)

#将连通的边按顺序排列 
#最后一个一定是一个开头，从最后一个开始依次找相邻的边           
def sort_edge_list(start_edge,edge_list):
    edge_list_temp=list(edge_list)
    edge_list_temp.remove(start_edge)

    for e in edge_list_temp:
        isconnected=start_edge.isConnectedTo(e) 
        if isconnected:
            sort_connected_edge_list.append(e)
            sort_edge_list(e,edge_list_temp)
            break
            
def sort_vtx_onedge(edge_list):
    
    v_list=[]
    e_index=1
    v_index=0
    
    for e in edge_list:
        vs=e.connectedVertices()
        if e_index>=len(edge_list):
            for v in vs:
                if v not in v_list:
                    v_list.append(v)
        elif e_index==1:
            for index in range(len(vs)):
                is_conected_edge=vs[index].isConnectedTo(edge_list[e_index])
                if is_conected_edge:
                    v_list.append(vs[index])
                else:
                    v_list.insert(0,vs[index])       
        else:
            for index in range(len(vs)):
                is_conected_edge=vs[index].isConnectedTo(edge_list[e_index])
                if is_conected_edge:
                    v_list.append(vs[index])
                
        e_index+=1
    return v_list

#计算连通边的总长度
def cal_edge_list_length(edge_list):
    len_list=[]
    total_len=0
    for e in edge_list:
        total_len+=e.getLength('world')
        len_list.append(total_len)
    return len_list
        
def average_vtx_onedge(edge_list,vtx_list,len_list):
    
    #len_list的最后一个就是整个连通边的总长度,除以边数，求平均每个边的长度
    average_len=len_list[len(len_list)-1]/len(len_list)
    edge_count=len(edge_list)
    vtx_count=len(vtx_list)
    new_vtx_pos_list=[]
    
    v_start_pos=dt.Point()
    v_end_pos=dt.Point()
    
    for v_index in range(1,vtx_count-1):
        total_average_len=average_len*v_index
        cur_edge_len=0
        
        for e_index in range(0,edge_count-1):
            if total_average_len<=len_list[0]:
                cur_edge_len=average_len/len_list[0]
                v_start_pos=vtx_list[0].getPosition('world')
                v_end_pos=vtx_list[1].getPosition('world')
                break
            if total_average_len>=len_list[e_index] and total_average_len<=len_list[e_index+1]:
                cur_edge_len=(total_average_len-len_list[e_index])/(len_list[e_index+1]-len_list[e_index])
                v_start_pos=vtx_list[e_index+1].getPosition('world')
                v_end_pos=vtx_list[e_index+2].getPosition('world')
                break
        
        new_x=v_start_pos.x+(v_end_pos.x-v_start_pos.x)*cur_edge_len
        new_y=v_start_pos.y+(v_end_pos.y-v_start_pos.y)*cur_edge_len
        new_z=v_start_pos.z+(v_end_pos.z-v_start_pos.z)*cur_edge_len
        new_point=dt.Point([new_x, new_y, new_z])  
        new_vtx_pos_list.append(new_point)

    
    return new_vtx_pos_list

    
def set_vtx_on_edge_list(vtx_list,new_vtx_pos_list):
    vtx_count=len(vtx_list)
    for v_index in range(1,vtx_count-1):
        vtx_list[v_index].setPosition(new_vtx_pos_list[v_index-1],'world')
        vtx_list[v_index].updateSurface()
      

esels = pm.selected()
dir(esels)
for esel in esels:
    for e in esel:
        g_sel_edge_list.append(e)
        g_sel_edge_list_temp.append(e)

while len(g_sel_edge_list_temp)!=0:
    
    sort_connected_edge_list=[]
    #添加第一个边，以这个边为起点找接下来的相连通的边
    e_temp=g_sel_edge_list_temp[0]
    connected_edge_list.append(e_temp)
    g_sel_edge_list_temp.remove(e_temp)
    
    get_connected_edge(e_temp,g_sel_edge_list)
    
    start_edge=connected_edge_list[len(connected_edge_list)-1]
    sort_edge_list(start_edge,connected_edge_list)
    sort_connected_edge_list.insert(0,start_edge)
    
    #给连通边的顶点排序
    sort_v_list=list(sort_vtx_onedge(sort_connected_edge_list))
    g_sort_vtx_dic[e_temp.index()]=sort_v_list
    
    g_connected_edge_dic[e_temp.index()]=sort_connected_edge_list
    connected_edge_list=[]
    g_conected_edge_index+=1
    
for key,value in g_connected_edge_dic.items():
    len_list=list(cal_edge_list_length(value))
    new_vtx_pos_list=average_vtx_onedge(value,g_sort_vtx_dic[key],len_list)
    set_vtx_on_edge_list(g_sort_vtx_dic[key],new_vtx_pos_list)
        


print g_connected_edge_dic
print g_sort_vtx_dic
    

            
        
            
            
    

    
