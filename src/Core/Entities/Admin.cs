namespace Core.Entities
{
    /// <summary>
    /// Representa un administrador del sistema.
    /// </summary>
    public class Admin
    {
        /// <summary>
        /// ID único del administrador.
        /// </summary>
        public int Id { get; set; }

        /// <summary>
        /// Nombre de usuario para el inicio de sesión. Debe ser único.
        /// </summary>
        public required string Username { get; set; }

        /// <summary>
        /// Hash de la contraseña del administrador.
        /// </summary>
        public required string HashedPassword { get; set; }

        /// <summary>
        /// Correo electrónico del administrador. Debe ser único.
        /// </summary>
        public required string Email { get; set; }

        /// <summary>
        /// Indica si la cuenta del administrador está activa.
        /// </summary>
        public bool IsActive { get; set; } = true;

        /// <summary>
        /// Indica si el administrador tiene privilegios de superadministrador.
        /// </summary>
        public bool IsSuperAdmin { get; set; } = false;
    }
}