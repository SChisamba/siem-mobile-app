from datetime import datetime

import flet as ft

import hashlib

import socket

import mysql.connector

# --- MOBILE REMOTE NETWORK CONFIGURATION ---
db_config = {
    'host': '192.168.43.104',  # Fallback baseline connection property
    'user': 'root',
    'password': 'ChIcHi_13TaKa',
    'database': 'cyber_security_system'
}


def get_local_ip():
    """Milestone: Proactive Deflection edge address locator."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except socket.error:
        return '127.0.0.1'


def hash_password(password):
    """Converts plain text into secure SHA-256 signatures."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


class MobileGatewayApp:
    def __init__(self):
        # ✅ DYNAMIC HOST CONFIGURATION INPUT COMPONENT
        self.ent_host_ip = ft.TextField(
            label='Database Laptop IP',
            value=db_config['host'],
            width=260,
            bgcolor='white10',
            border_color='orange700'
        )
        self.ent_user = ft.TextField(
            label='Username',
            width=260,
            bgcolor='white10',
            border_color='blue700'
        )
        self.ent_pass = ft.TextField(
            label='Password',
            password=True,
            can_reveal_password=True,
            width=260,
            bgcolor='white10',
            border_color='blue700'
        )
        self.lbl_status = ft.Text(
            value='',
            size=14,
            color='orange',
            text_align=ft.TextAlign.CENTER
        )

    def main(self, page: ft.Page):
        page.title = 'Remote Access Terminal v2.0'
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.window_width = 380
        page.window_height = 640
        page.bgcolor = 'bluegrey900'

        card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        value='🔐 Mobile Gateway Node',
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color='white'
                    ),
                    ft.Divider(color='bluegrey700'),
                    self.ent_host_ip,  # Dynamic IP textbox rendered on UI
                    ft.Divider(color='bluegrey700', height=5),
                    self.ent_user,
                    self.ent_pass,
                    self.lbl_status,
                    ft.FilledButton(
                        content=ft.Text('Verify Access Identity'),
                        on_click=lambda e: self.process_mobile_login(page),
                        style=ft.ButtonStyle(bgcolor='blue700')
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12
            ),
            padding=25,
            bgcolor='black54',
            border_radius=15,
            width=320
        )

        page.add(card)

    def process_mobile_login(self, page: ft.Page):
        # ✅ INTERCEPT HOOK: Dynamically remaps database host properties
        typed_ip = self.ent_host_ip.value.strip()
        if not typed_ip:
            self.lbl_status.value = 'Target IP parameters required.'
            page.update()
            return
            
        db_config['host'] = typed_ip
        
        username = self.ent_user.value.strip()
        password = self.ent_pass.value.strip()
        ip_address = get_local_ip()

        if not username or not password:
            self.lbl_status.value = 'Fields cannot be empty.'
            page.update()
            return

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            current_time = datetime.now()

            # --- 1. FIREWALL BLACKLIST VERIFICATION ---
            q_block = (
                "SELECT reason, expires_at FROM blocked_ips "
                "WHERE ip_address = %s"
            )
            cursor.execute(q_block, (ip_address,))
            block_record = cursor.fetchone()

            if block_record:
                reason, expires_at = block_record
                if current_time < expires_at:
                    self.lbl_status.value = 'PROACTIVE DROP: IP Isolated.'
                    page.update()
                    return
                else:
                    del_q = (
                        "DELETE FROM blocked_ips "
                        "WHERE ip_address = %s"
                    )
                    cursor.execute(del_q, (ip_address,))
                    conn.commit()

            # --- 2. CRYPTOGRAPHIC CREDENTIAL MATCH ENGINE ---
            secure_input_hash = hash_password(password)
            q_user = "SELECT password_hash FROM users WHERE username = %s"
            cursor.execute(q_user, (username,))
            user_record = cursor.fetchone()

            db_hash = user_record[0] if user_record else None

            if db_hash and db_hash == secure_input_hash:
                ins_ok = (
                    "INSERT INTO login_logs "
                    "(username, ip_address, status, details) "
                    "VALUES (%s, %s, 'SUCCESS', 'Mobile Terminal Entry')"
                )
                cursor.execute(ins_ok, (username, ip_address))
                conn.commit()
                self.lbl_status.value = f'Welcome back, {username}!'
                self.ent_user.value = ''
                self.ent_pass.value = ''
            else:
                # --- 3. INTRUSION TRACKING & LOG INSERTION ---
                ins_fail = (
                    "INSERT INTO login_logs "
                    "(username, ip_address, status, details) "
                    "VALUES (%s, %s, 'FAILED', 'Mobile Attack Signature')"
                )
                cursor.execute(ins_fail, (username, ip_address))
                conn.commit()

                q_count = (
                    "SELECT COUNT(*) FROM login_logs "
                    "WHERE ip_address = %s AND status = 'FAILED' "
                    "AND timestamp > NOW() - INTERVAL 3 MINUTE"
                )
                cursor.execute(q_count, (ip_address,))
                count_record = cursor.fetchone()
                failed_count = count_record[0] if count_record else 0

                if failed_count >= 3:
                    ins_ban = (
                        "INSERT IGNORE INTO blocked_ips "
                        "(ip_address, reason, expires_at) "
                        "VALUES (%s, 'IDS Mobile Threat Lockdown', "
                        "NOW() + INTERVAL 1 MINUTE)"
                    )
                    cursor.execute(ins_ban, (ip_address,))
                    conn.commit()
                    self.lbl_status.value = 'FIREWALL WALL ENGAGED: Banned.'
                else:
                    fail_count_str = format(failed_count)
                    self.lbl_warning.config(
                        text=(
                            f'Auth Failure. '
                            f'Lockout in ({fail_count_str}/3) events.'
                        )
                    )

        except mysql.connector.Error:
            self.lbl_status.value = 'Network Pipeline Sync Error.'
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None:
                conn.close()

        page.update()


# --- BOOTSTRAP INITIALIZATION ENVIRONMENT ---
# This statement rests flush against the absolute left wall of the page!
if __name__ == '__main__':
    app_instance = MobileGatewayApp()
    # ✅ FIX: Passes native mobile container 
    # targets to compile correctly on the phone
    ft.app(target=app_instance.main)
    