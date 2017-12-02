import math

def create_bg_topic_and_end_topic(luong_number,topic_per_thread,so_topic):
    begin_topic = luong_number*topic_per_thread + 1
    end_topic = luong_number*topic_per_thread + topic_per_thread
    if end_topic > so_topic:
        end_topic = so_topic
    return begin_topic,end_topic

if __name__ =='__main__':
    so_luong = 5
    so_topic = 31.0
    topic_per_thread = int(math.ceil(so_topic/so_luong))
    print topic_per_thread
#     for luong_number in range(0,so_luong):
#         begin_topic,end_topic=create_bg_topic_and_end_topic(luong_number,topic_per_thread,so_topic)
#         print luong_number,begin_topic,end_topic
    begin_topic,end_topic=create_bg_topic_and_end_topic(2,topic_per_thread,so_topic)
    for i in range(begin_topic,end_topic+1):
        print i