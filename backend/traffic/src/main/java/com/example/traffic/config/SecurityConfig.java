package com.example.traffic.config;

import com.example.traffic.security.CustomUserDetailsService;
import com.example.traffic.security.JwtAuthenticationFilter;
import com.example.traffic.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtTokenProvider jwtTokenProvider;
    private final CustomUserDetailsService customUserDetailsService;

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .cors(cors -> cors.configurationSource(corsConfigurationSource()))
                .csrf(AbstractHttpConfigurer::disable)
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                        .requestMatchers("/api/auth/**").permitAll()
                        .requestMatchers("/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html").permitAll()

                        // FastAPI internal ingestion endpoint. Controller checks X-Internal-Api-Key.
                        .requestMatchers(HttpMethod.POST, "/api/v1/detection-logs").permitAll()
                        .requestMatchers(HttpMethod.POST, "/api/speed-violations").permitAll()

                        // TODO(frontend-integration): Temporary permitAll for Vue first-pass integration.
                        // Remove this GET rule after JWT login is wired from Vue and protect it with authenticated().
                        .requestMatchers(HttpMethod.GET, "/api/v1/detection-logs/**").permitAll()
                        // TODO(frontend-integration): Temporary permitAll for Vue flow count dashboard integration.
                        // Remove this GET rule after JWT login is wired from Vue and protect it with authenticated().
                        .requestMatchers(HttpMethod.GET, "/api/flow-events/stats/count").permitAll()
                        // TODO(frontend-integration): Temporary permitAll for Vue camera/zone dashboard integration.
                        // Remove these GET rules after JWT login is wired from Vue and protect them with authenticated().
                        .requestMatchers(HttpMethod.GET, "/api/zones").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/cameras").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/cameras/**").permitAll()
                        // TODO(frontend-integration): Temporary permitAll for Vue hourly stats dashboard integration.
                        // Remove this GET rule after JWT login is wired from Vue and protect it with authenticated().
                        .requestMatchers(HttpMethod.GET, "/api/stats/hourly").permitAll()

                        // Notice permissions
                        .requestMatchers(HttpMethod.GET, "/api/notices/**").permitAll()
                        .requestMatchers("/api/notices/**").hasRole("ADMIN")

                        // Post permissions
                        .requestMatchers(HttpMethod.GET, "/api/posts/**").permitAll()

                        // QnA permissions
                        .requestMatchers(HttpMethod.GET, "/api/qna/**").permitAll()
                        .requestMatchers(HttpMethod.POST, "/api/qna/questions/*/answers").hasRole("ADMIN")
                        .requestMatchers("/api/qna/**").authenticated()

                        .anyRequest().authenticated()
                )
                .addFilterBefore(new JwtAuthenticationFilter(jwtTokenProvider, customUserDetailsService),
                        UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(List.of(
                "http://localhost:5173",
                "http://127.0.0.1:5173"
        ));
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(List.of("Authorization", "Content-Type", "X-Internal-Api-Key"));
        configuration.setExposedHeaders(List.of("Authorization"));
        configuration.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
