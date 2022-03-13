import sqlite3
conn = sqlite3.connect("data_aq.db", check_same_thread=False)
c = conn.cursor()



def create_table_aq():
    c.execute('CREATE TABLE IF NOT EXISTS aqtable(aq_id INT, thk_aq INT, baseflow INT, porosity INT, hyd_con INT, ref_head INT)')

def add_data_aq(aq_id, thk_aq, baseflow, porosity, hyd_con, ref_head):
    c.execute('INSERT INTO aqtable(aq_id, thk_aq, baseflow, porosity, hyd_con, ref_head) VALUES (?,?,?,?,?,?)', (aq_id, thk_aq, baseflow, porosity, hyd_con, ref_head))
    conn.commit()

def view_all_data_aq():
    c.execute('SELECT * FROM aqtable')
    data = c.fetchall()
    return data

def view_unique_data_aq():
    c.execute('SELECT DISTINCT aq_id FROM aqtable')
    data = c.fetchall()
    return data

def get_id_aq(aq_id):
    c.execute('SELECT * FROM aqtable WHERE aq_id="{}"'.format(aq_id))  
    data = c.fetchall()
    return data

def edit_aq_id(new_aq_id, new_thk_aq, new_baseflow, new_porosity, new_hyd_con, new_ref_head, aq_id, thk_aq, baseflow, porosity, hyd_con, ref_head):
    c.execute("UPDATE aqtable SET aq_id=?, thk_aq=?, baseflow=?, porosity=?, hyd_con=?, ref_head=? WHERE aq_id=? and thk_aq=? and baseflow=? and porosity=? and hyd_con=? and ref_head=?", (new_aq_id, new_thk_aq, new_baseflow, new_porosity, new_hyd_con, new_ref_head, aq_id, thk_aq, baseflow, porosity, hyd_con, ref_head) )
    conn.commit()
    data = c.fetchall()
    return data

def delete_id_aq(aq_id):
    c.execute('DELETE FROM aqtable WHERE aq_id="{}"'.format(aq_id))
    conn.commit()
