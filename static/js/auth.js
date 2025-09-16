// // // Hàm lưu trữ thông tin đăng nhập sau khi đăng nhập thành công
// // // function saveLoginState(data) {
// // //     try {
// // //         // Lưu trữ toàn bộ dữ liệu người dùng (trừ mật khẩu và refresh token)
// // //         const userProfile = {
// // //             access_token: data.access_token,
// // //             id: data.user.id,
// // //             phone_number: data.phone_number,
// // //             name: data.user.name,
// // //             address: data.address,
// // //             dob: data.dob,
// // //             email: data.email,
// // //             avatar: data.avatar
            
// // //         };
// // //         localStorage.setItem('userProfile', JSON.stringify(userProfile));
// // //         localStorage.setItem('isLoggedIn', 'true');
// // //         // Lưu refresh token riêng để bảo mật và sử dụng khi cần refresh token
// // //         localStorage.setItem('refreshToken', data.refresh_token);
// // //         console.log("name",userProfile.name)
// // //         console.log("avatar",userProfile.avatar)
// // //         console.log('Thông tin người dùng và trạng thái đăng nhập đã được lưu.');
// // //     } catch (error) {
// // //         console.error('Lỗi khi lưu trữ thông tin đăng nhập:', error);
// // //     }
// // // }

// // // Hàm lưu trữ thông tin đăng nhập sau khi đăng nhập thành công
// // function saveLoginState(data) {
// //     try {
// //         const user = data.user || data; // Lấy đối tượng user, hoặc toàn bộ data nếu không có trường user

// //         const userProfile = {
// //             access_token: data.access_token,
// //             id: data.user.id,
// //             phone_number: data.phone_number,
// //             name: data.user.name,
// //             address: data.address,
// //             dob: data.dob,
// //             email: data.email,
// //             avatar: data.user.avatar || data.avatar
            
// //         };
// //         localStorage.setItem('userProfile', JSON.stringify(userProfile));
// //         localStorage.setItem('isLoggedIn', 'true');
// //         localStorage.setItem('refreshToken', data.refresh_token);
        
// //         console.log("name", userProfile.name);
// //         console.log("avatar", userProfile.avatar);
// //         console.log('Thông tin người dùng và trạng thái đăng nhập đã được lưu.');
// //     } catch (error) {
// //         console.error('Lỗi khi lưu trữ thông tin đăng nhập:', error);
// //     }
// // }

// // // Hàm lấy access token
// // function getAccessToken() {
// //     const userProfile = localStorage.getItem('userProfile');
// //     return userProfile ? JSON.parse(userProfile).access_token : null;
// // }

// // // Hàm lấy refresh token
// // function getRefreshToken() {
// //     return localStorage.getItem('refreshToken');
// // }

// // // Hàm lấy thông tin người dùng
// // function getUserProfile() {
// //     const userProfile = localStorage.getItem('userProfile');
// //     return userProfile ? JSON.parse(userProfile) : null;
// // }

// // // Hàm kiểm tra trạng thái đăng nhập
// // function isLoggedIn() {
// //     return localStorage.getItem('isLoggedIn') === 'true' && !!getAccessToken();
// // }

// // // Hàm đăng xuất
// // function logout() {
// //     localStorage.removeItem('userProfile');
// //     localStorage.removeItem('refreshToken');
// //     localStorage.removeItem('isLoggedIn');
// //     console.log('Tất cả thông tin đăng nhập đã được xóa.');
// // }


// // Hàm lưu trữ thông tin đăng nhập sau khi đăng nhập thành công
// function saveLoginState(data) {
//     try {
//         // Kiểm tra xem dữ liệu người dùng nằm trong 'data.user' hay trực tiếp trong 'data'
//         const user = data.user || data;

//         const userProfile = {
//             access_token: data.access_token,
//             refresh_token: data.refresh_token,
//             id: user.id,
//             phone_number: user.phone_number,
//             name: user.name,
//             address: user.address,
//             dob: user.dob,
//             email: user.email,
//             avatar: user.avatar
//         };

//         localStorage.setItem('userProfile', JSON.stringify(userProfile));
//         localStorage.setItem('isLoggedIn', 'true');
//         // Lưu refresh token riêng
//         localStorage.setItem('refreshToken', data.refresh_token);
        
//         console.log("name", userProfile.name);
//         console.log("avatar", userProfile.avatar);
//         console.log('Thông tin người dùng và trạng thái đăng nhập đã được lưu.');
//     } catch (error) {
//         console.error('Lỗi khi lưu trữ thông tin đăng nhập:', error);
//     }
// }

// // Hàm lấy access token
// function getAccessToken() {
//     const userProfile = localStorage.getItem('userProfile');
//     return userProfile ? JSON.parse(userProfile).access_token : null;
// }

// // Hàm lấy refresh token
// function getRefreshToken() {
//     return localStorage.getItem('refreshToken');
// }

// // Hàm lấy thông tin người dùng
// function getUserProfile() {
//     const userProfile = localStorage.getItem('userProfile');
//     return userProfile ? JSON.parse(userProfile) : null;
// }

// // Hàm kiểm tra trạng thái đăng nhập
// function isLoggedIn() {
//     return localStorage.getItem('isLoggedIn') === 'true' && !!getAccessToken();
// }

// // Hàm đăng xuất
// function logout() {
//     localStorage.removeItem('userProfile');
//     localStorage.removeItem('refreshToken');
//     localStorage.removeItem('isLoggedIn');
//     console.log('Tất cả thông tin đăng nhập đã được xóa.');
// }



// file auth.js:
function saveLoginState(data) {
    try {
        const user = data.user || data;

        const userProfile = {
            access_token: data.access_token,
            refresh_token: data.refresh_token,
            id: user.id,
            phone_number: user.phone_number,
            name: user.name,
            address: user.address,
            dob: user.dob,
            email: user.email,
            avatar: user.avatar
        };

        localStorage.setItem('userProfile', JSON.stringify(userProfile));
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('refreshToken', data.refresh_token);
        
        console.log("name", userProfile.name);
        console.log("avatar", userProfile.avatar);
        console.log('Thông tin người dùng và trạng thái đăng nhập đã được lưu.');
    } catch (error) {
        console.error('Lỗi khi lưu trữ thông tin đăng nhập:', error);
    }
}

function getAccessToken() {
    const userProfile = localStorage.getItem('userProfile');
    return userProfile ? JSON.parse(userProfile).access_token : null;
}

function getRefreshToken() {
    return localStorage.getItem('refreshToken');
}

function getUserProfile() {
    const userProfile = localStorage.getItem('userProfile');
    return userProfile ? JSON.parse(userProfile) : null;
}

function isLoggedIn() {
    return localStorage.getItem('isLoggedIn') === 'true' && !!getAccessToken();
}

function logout() {
    localStorage.removeItem('userProfile');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('isLoggedIn');
    console.log('Tất cả thông tin đăng nhập đã được xóa.');
}