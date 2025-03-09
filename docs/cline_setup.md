# Cline Setup Documentation

## Important Note
This documentation is specifically for setting up this project with Cline on different machines (laptop/desktop). Since Cline does not sync settings between devices, these steps must be performed on each new machine.

## Initial Setup Steps

1. **Environment Setup**
   - Clone the repository to your local machine
   - Ensure Python 3.12.x is installed
   - Set up a virtual environment as described in `setup.md`

2. **BWS Executable Setup**
   - Download: https://github.com/bitwarden/sdk-sm/releases/download/bws-v1.0.0/bws-x86_64-pc-windows-msvc-1.0.0.zip
   - Extract to the `tools` directory in your project
   - Verify `tools/bws.exe` exists and has correct permissions

3. **Cline Configuration Per Machine**

   a. Environment Variables
   ```dotenv
   BWS_ACCESS_TOKEN=[your-bws-access-token]
   PROJECT_ID=[your-project-id]
   ```
   - Create `.env` file in project root
   - Add above variables with your specific values
   - Keep tokens secure and never commit to version control

   b. Python Environment
   - Create fresh virtual environment for this machine
   - Install all dependencies from requirements files
   - Verify pytest and other tools are working

## Verification Steps

1. **Check BWS Setup**
   ```bash
   # Should show connection successful
   pytest src/test/test_bws.py -v
   ```

2. **Verify Environment**
   - Confirm `.env` file exists with correct values
   - Check virtual environment is activated
   - Test all dependencies are installed correctly

## Common Issues

1. **BWS Executable Problems**
   - Ensure using correct version from specified GitHub release
   - Check file permissions
   - Verify PATH if needed

2. **Environment Issues**
   - Double-check .env values
   - Ensure virtual environment is active
   - Verify Python version matches project requirements

3. **Package Conflicts**
   - Use clean virtual environment
   - Install requirements in correct order
   - Check for version mismatches

## Best Practices

1. **Version Control**
   - Don't commit .env files
   - Keep BWS executable in tools directory
   - Document any machine-specific configurations

2. **Security**
   - Keep access tokens secure
   - Don't share credentials between environments
   - Regularly rotate tokens if needed

3. **Maintenance**
   - Update documentation for any changes
   - Keep track of different machine setups
   - Document any special configurations needed
