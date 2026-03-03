import tkinter as tk
from tkinter import ttk, messagebox
import core

class GymApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Gimnasio - Control de Pagos (Offline)')
        self.geometry('980x640')
        self.minsize(900, 600)
        self.data = core.load_db()

        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True)
        self.tab_dash = ttk.Frame(nb); nb.add(self.tab_dash, text='Pendientes')
        self.tab_reg = ttk.Frame(nb); nb.add(self.tab_reg, text='Registrar')
        self.tab_cli = ttk.Frame(nb); nb.add(self.tab_cli, text='Clientes')
        self.tab_cfg = ttk.Frame(nb); nb.add(self.tab_cfg, text='Configuración')
        self.tab_exp = ttk.Frame(nb); nb.add(self.tab_exp, text='Exportar')
        self._build_dash(self.tab_dash)
        self._build_reg(self.tab_reg)
        self._build_cli(self.tab_cli)
        self._build_cfg(self.tab_cfg)
        self._build_exp(self.tab_exp)

    def _build_dash(self, parent):
        top = ttk.Frame(parent); top.pack(fill='x', pady=6, padx=8)
        ttk.Label(top, text='Resumen de pendientes').pack(side='left')
        ttk.Button(top, text='Actualizar', command=self.refresh_all).pack(side='right')
        body = ttk.Frame(parent); body.pack(fill='both', expand=True, padx=8, pady=6)
        self.tree_atras = self._make_tree(body, 'Atrasados')
        self.tree_hoy   = self._make_tree(body, 'Vencen hoy')
        self.tree_prox  = self._make_tree(body, 'Próximos')
        btns = ttk.Frame(parent); btns.pack(fill='x', padx=8, pady=6)
        ttk.Button(btns, text='Cobrar seleccionado', command=self.cobrar_desde_dashboard).pack(side='left')

    def _make_tree(self, parent, title):
        frm = ttk.Labelframe(parent, text=title); frm.pack(side='left', fill='both', expand=True, padx=4, pady=4)
        cols = ('id','nombre','plan','precio','vence')
        tree = ttk.Treeview(frm, columns=cols, show='headings', height=10)
        for c, w in zip(cols, (50, 200, 90, 90, 110)):
            tree.heading(c, text=c.capitalize())
            tree.column(c, width=w, anchor='center')
        vsb = ttk.Scrollbar(frm, orient='vertical', command=tree.yview)
        tree.configure(yscroll=vsb.set)
        tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        return tree

    def cobrar_desde_dashboard(self):
        tree = None
        for t in (self.tree_atras, self.tree_hoy, self.tree_prox):
            if t.selection():
                tree = t; break
        if not tree:
            messagebox.showinfo('Cobrar', 'Selecciona un cliente en alguna lista.'); return
        cid = int(tree.item(tree.selection()[0], 'values')[0])
        self._cobrar_por_id(cid)

    def _build_reg(self, parent):
        frm = ttk.Frame(parent); frm.pack(padx=12, pady=12, fill='x')
        ttk.Label(frm, text='Nombre:').grid(row=0, column=0, sticky='e', padx=4, pady=4)
        self.ent_nombre = ttk.Entry(frm, width=40); self.ent_nombre.grid(row=0, column=1, columnspan=3, sticky='w', padx=4, pady=4)
        ttk.Label(frm, text='Plan:').grid(row=1, column=0, sticky='e', padx=4, pady=4)
        self.plan_var = tk.StringVar(value='mensual')
        ttk.Radiobutton(frm, text='Semanal', variable=self.plan_var, value='semanal', command=self._sync_precio_por_defecto).grid(row=1, column=1, sticky='w')
        ttk.Radiobutton(frm, text='Mensual', variable=self.plan_var, value='mensual', command=self._sync_precio_por_defecto).grid(row=1, column=2, sticky='w')
        ttk.Label(frm, text='Precio:').grid(row=2, column=0, sticky='e', padx=4, pady=4)
        self.ent_precio = ttk.Entry(frm, width=12); self.ent_precio.grid(row=2, column=1, sticky='w', padx=4, pady=4)
        ttk.Label(frm, text='Fecha de inicio (dd/mm/aaaa):').grid(row=3, column=0, sticky='e', padx=4, pady=4)
        self.ent_fecha = ttk.Entry(frm, width=16); self.ent_fecha.grid(row=3, column=1, sticky='w', padx=4, pady=4)
        ttk.Button(frm, text='Registrar', command=self._registrar_cliente).grid(row=4, column=1, sticky='w', pady=8)
        self.lbl_reg_status = ttk.Label(frm, text=''); self.lbl_reg_status.grid(row=5, column=0, columnspan=4, sticky='w')
        self._sync_fecha_hoy(); self._sync_precio_por_defecto()

    def _sync_fecha_hoy(self):
        self.ent_fecha.delete(0, 'end'); self.ent_fecha.insert(0, core.fmt_show(core.hoy()))

    def _sync_precio_por_defecto(self):
        cfg = self.data['configs']
        precio = cfg['precio_semanal'] if self.plan_var.get()=='semanal' else cfg['precio_mensual']
        self.ent_precio.delete(0, 'end'); self.ent_precio.insert(0, f'{precio:.2f}')

    def _registrar_cliente(self):
        nombre = self.ent_nombre.get().strip()
        if not nombre:
            messagebox.showerror('Error', 'El nombre no puede estar vacío.'); return
        plan = self.plan_var.get()
        try:
            precio = float(self.ent_precio.get().strip().replace(',', '.'))
        except ValueError:
            messagebox.showerror('Error', 'Precio inválido.'); return
        try:
            f = core.parse_date_input(self.ent_fecha.get())
        except Exception as e:
            messagebox.showerror('Error', str(e)); return
        cli = core.registrar_cliente(self.data, nombre, plan, precio, f)
        self.lbl_reg_status.config(text=f"Registrado: ID {cli['id']} | Próximo pago: {core.fmt_show(core.parse_date_input(cli['proximo_pago']))}")
        self.ent_nombre.delete(0, 'end'); self._sync_precio_por_defecto(); self._sync_fecha_hoy(); self.refresh_all()

    def _build_cli(self, parent):
        top = ttk.Frame(parent); top.pack(fill='x', padx=8, pady=6)
        ttk.Label(top, text='Buscar:').pack(side='left')
        self.ent_buscar = ttk.Entry(top, width=30); self.ent_buscar.pack(side='left', padx=4)
        ttk.Button(top, text='Ir', command=self._buscar_clientes).pack(side='left')
        ttk.Button(top, text='Mostrar todos', command=self._load_clientes).pack(side='left', padx=6)
        ttk.Button(top, text='Cobrar seleccionado', command=self.cobrar_desde_clientes).pack(side='right')
        ttk.Button(top, text='Activar/Inactivar', command=self.toggle_estado).pack(side='right', padx=6)
        cols = ('id','nombre','plan','precio','proximo','estado')
        self.tree_cli = ttk.Treeview(parent, columns=cols, show='headings')
        for c, w in zip(cols, (50, 220, 90, 90, 110, 90)):
            self.tree_cli.heading(c, text=c.capitalize()); self.tree_cli.column(c, width=w, anchor='center')
        vsb = ttk.Scrollbar(parent, orient='vertical', command=self.tree_cli.yview)
        self.tree_cli.configure(yscroll=vsb.set)
        self.tree_cli.pack(side='left', fill='both', expand=True, padx=8, pady=6); vsb.pack(side='left', fill='y')

    def _load_clientes(self, lista=None):
        if lista is None: lista = core.listar_clientes(self.data)
        for i in self.tree_cli.get_children(): self.tree_cli.delete(i)
        for c in lista:
            due = core.parse_date_input(c['proximo_pago']); estado = 'ACTIVO' if c.get('activo', True) else 'INACTIVO'
            self.tree_cli.insert('', 'end', values=(c['id'], c['nombre'], c['plan'], f"${float(c['precio']):.2f}", core.fmt_show(due), estado))

    def _buscar_clientes(self):
        self._load_clientes(core.buscar(self.data, self.ent_buscar.get()))

    def cobrar_desde_clientes(self):
        sel = self.tree_cli.selection()
        if not sel: messagebox.showinfo('Cobrar', 'Selecciona un cliente.'); return
        cid = int(self.tree_cli.item(sel[0], 'values')[0]); self._cobrar_por_id(cid)

    def toggle_estado(self):
        sel = self.tree_cli.selection()
        if not sel: messagebox.showinfo('Estado', 'Selecciona un cliente.'); return
        cid = int(self.tree_cli.item(sel[0], 'values')[0])
        for c in self.data['clientes']:
            if c['id'] == cid:
                actual = c.get('activo', True); break
        core.toggle_activo(self.data, cid, not actual); self.refresh_all()

    def _build_cfg(self, parent):
        frm = ttk.Frame(parent); frm.pack(padx=12, pady=12, anchor='nw')
        self.cfg_sem = tk.StringVar(); self.cfg_men = tk.StringVar(); self.cfg_dias = tk.StringVar()
        ttk.Label(frm, text='Precio semanal por defecto:').grid(row=0, column=0, sticky='e', padx=4, pady=4)
        ttk.Entry(frm, textvariable=self.cfg_sem, width=12).grid(row=0, column=1, sticky='w')
        ttk.Label(frm, text='Precio mensual por defecto:').grid(row=1, column=0, sticky='e', padx=4, pady=4)
        ttk.Entry(frm, textvariable=self.cfg_men, width=12).grid(row=1, column=1, sticky='w')
        ttk.Label(frm, text='Días "próximos" para vencimientos:').grid(row=2, column=0, sticky='e', padx=4, pady=4)
        ttk.Entry(frm, textvariable=self.cfg_dias, width=12).grid(row=2, column=1, sticky='w')
        ttk.Button(frm, text='Guardar configuración', command=self._guardar_cfg).grid(row=3, column=1, sticky='w', pady=8)

    def _guardar_cfg(self):
        try:
            ps = float(self.cfg_sem.get().replace(',', '.')); pm = float(self.cfg_men.get().replace(',', '.')); dp = int(self.cfg_dias.get())
        except ValueError:
            messagebox.showerror('Error', 'Revisa los valores ingresados.'); return
        core.actualizar_config(self.data, ps, pm, dp); messagebox.showinfo('Configuración', 'Configuración guardada.'); self._sync_precio_por_defecto(); self.refresh_all()

    def _build_exp(self, parent):
        frm = ttk.Frame(parent); frm.pack(padx=12, pady=12, anchor='nw')
        ttk.Label(frm, text='Exporta tus clientes a CSV para abrir en Excel.').grid(row=0, column=0, sticky='w')
        ttk.Button(frm, text='Exportar CSV', command=self._exportar).grid(row=1, column=0, sticky='w', pady=8)
        self.lbl_exp = ttk.Label(frm, text=''); self.lbl_exp.grid(row=2, column=0, sticky='w')

    def _exportar(self):
        path = core.exportar_csv(self.data); self.lbl_exp.config(text=f'Archivo creado: {path}'); messagebox.showinfo('Exportar', f'Se creó el archivo:\n{path}')

    def refresh_all(self):
        for tree in (self.tree_atras, self.tree_hoy, self.tree_prox):
            for i in tree.get_children(): tree.delete(i)
        atras, hoy_l, prox = core.get_pendientes(self.data)
        for lst, tree in ((atras, self.tree_atras), (hoy_l, self.tree_hoy), (prox, self.tree_prox)):
            for c in lst:
                due = core.parse_date_input(c['proximo_pago'])
                tree.insert('', 'end', values=(c['id'], c['nombre'], c['plan'], f"${float(c['precio']):.2f}", core.fmt_show(due)))
        self._load_clientes(); cfg = self.data['configs']
        self.cfg_sem.set(f"{cfg['precio_semanal']:.2f}"); self.cfg_men.set(f"{cfg['precio_mensual']:.2f}"); self.cfg_dias.set(str(cfg['dias_proximos']))

    def _cobrar_por_id(self, cid: int):
        cli = next((c for c in self.data['clientes'] if c['id']==cid), None)
        if not cli: messagebox.showerror('Error', 'Cliente no encontrado'); return
        info = core.calcular_cobro(cli)
        if 'error' in info: messagebox.showerror('Error', info['error']); return
        msg = (f"Cliente: {cli['nombre']} (ID {cli['id']})\n"
               f"Plan: {cli['plan']} | Precio por periodo: ${float(cli['precio']):.2f}\n"
               f"{info['mensaje']}\n"
               f"Monto a cobrar ahora: ${info['monto']:.2f}\n"
               f"Próxima fecha de pago tras cobro: {core.fmt_show(info['nuevo_due'])}\n\n¿Confirmar cobro?")
        if messagebox.askyesno('Cobrar / Renovar', msg):
            core.aplicar_cobro(self.data, cid, info['nuevo_due']); messagebox.showinfo('Cobro', 'Cobro registrado y próxima fecha actualizada.'); self.refresh_all()

if __name__ == '__main__':
    app = GymApp(); app.mainloop()
