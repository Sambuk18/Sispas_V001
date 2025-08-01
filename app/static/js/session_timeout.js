document.addEventListener('DOMContentLoaded', function() {
    let timeoutWarning;
    let timeoutLogout;
    const warningTime = 1 * 60 * 1000; // 1 minutos de advertencia
    const logoutTime = 10 * 60 * 1000; // 10 minutos para logout
    
    function resetTimers() {
        clearTimeout(timeoutWarning);
        clearTimeout(timeoutLogout);
        
        timeoutWarning = setTimeout(showTimeoutWarning, logoutTime - warningTime);
        timeoutLogout = setTimeout(logout, logoutTime);
    }
    
    function showTimeoutWarning() {
        // Mostrar modal de advertencia
        const modal = document.createElement('div');
        modal.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                        background: rgba(0,0,0,0.5); z-index: 1000; display: flex; 
                        justify-content: center; align-items: center;">
                <div style="background: white; padding: 20px; border-radius: 5px; max-width: 500px;">
                    <h3>Tu sesión está a punto de expirar</h3>
                    <p>Serás desconectado por inactividad en 5 minutos. ¿Deseas continuar?</p>
                    <button id="continueSession">Sí, continuar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        document.getElementById('continueSession').addEventListener('click', function() {
            document.body.removeChild(modal);
            resetTimers();
            // Enviar petición al servidor para mantener la sesión activa
            fetch('/keepalive', {method: 'POST'});
        });
    }
    
    function logout() {
        fetch('/logout', {method: 'POST'})
            .then(() => window.location.href = '/login?timeout=1');
    }
    
    // Eventos que resetearán el temporizador
    window.onload = resetTimers;
    window.onmousemove = resetTimers;
    window.onmousedown = resetTimers;
    window.ontouchstart = resetTimers;
    window.onkeypress = resetTimers;
    
    resetTimers();
});